"""One environment configuration boundary; exception text never contains values."""

import os
import re
from pathlib import Path
from typing import Literal, Self
from urllib.parse import parse_qsl, urlsplit

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, model_validator

BACKEND_ROOT = Path(__file__).resolve().parents[1]
NASA_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
ProviderName = Literal["nasa_power", "open_meteo"]
UNSAFE_TLS_OPTIONS = {
    ("tls", "false"),
    ("ssl", "false"),
    ("tlsinsecure", "true"),
    ("tlsallowinvalidcertificates", "true"),
    ("tlsallowinvalidhostnames", "true"),
}


class ConfigurationError(RuntimeError):
    """Safe configuration failure, without rejected values or paths."""


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True, extra="forbid")
    mongodb_uri: SecretStr
    mongodb_database: str = Field(
        default="climate_hazard_analyzer", pattern=r"^[A-Za-z0-9_-]{1,63}$"
    )
    mongodb_timeout_ms: int = Field(default=5000, ge=100, le=30000)

    @model_validator(mode="after")
    def validate_uri(self) -> Self:
        uri = self.mongodb_uri.get_secret_value()
        try:
            parsed = urlsplit(uri)
            if (
                parsed.scheme != "mongodb+srv"
                or not (parsed.hostname or "").endswith(".mongodb.net")
                or not parsed.username
                or not parsed.password
                or parsed.port is not None
                or parsed.fragment
                or uri.count("@") != 1
                or re.search(r"\s|[<>]|%(?![0-9A-Fa-f]{2})", uri)
            ):
                raise ValueError
            # PyMongo also splits options on ";", and any duplicate occurrence may win.
            query = parsed.query.replace(";", "&")
            options = {(k.lower(), v.lower()) for k, v in parse_qsl(query)}
            if options & UNSAFE_TLS_OPTIONS:
                raise ValueError
        except ValueError:
            raise ValueError("MONGODB_URI must be a valid, TLS-verified Atlas SRV URI") from None
        return self


class WeatherSettings(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True, extra="forbid")
    weather_primary_provider: ProviderName = "nasa_power"
    weather_fallback_providers: tuple[ProviderName, ...] = ("open_meteo",)
    weather_fallback_enabled: bool = False
    open_meteo_noncommercial_use: bool = False
    nasa_power_base_url: Literal[NASA_URL] = NASA_URL
    nasa_power_time_standard: Literal["UTC"] = "UTC"
    open_meteo_base_url: Literal[OPEN_METEO_URL] = OPEN_METEO_URL
    open_meteo_model: Literal["era5"] = "era5"
    weather_provider_timeout_seconds: float = Field(default=10, ge=0.1, le=30)
    weather_provider_max_retries: int = Field(default=1, ge=0, le=2)
    weather_total_timeout_seconds: float = Field(default=60, ge=1, le=90)
    weather_min_coverage_percent: float = Field(default=95, ge=95, le=100)

    @property
    def provider_order(self) -> tuple[ProviderName, ...]:
        names = (self.weather_primary_provider,)
        if self.weather_fallback_enabled:
            names += self.weather_fallback_providers
        return tuple(dict.fromkeys(names))

    @model_validator(mode="after")
    def check_free_usage(self) -> Self:
        if "open_meteo" in self.provider_order and not self.open_meteo_noncommercial_use:
            raise ValueError("Open-Meteo free access requires non-commercial usage confirmation")
        return self


def environment(env_file: Path = BACKEND_ROOT / ".env") -> dict[str, str | None]:
    # Disable interpolation so a private file cannot expand unrelated environment secrets.
    try:
        local = dotenv_values(env_file, interpolate=False) if env_file.is_file() else {}
    except (OSError, UnicodeDecodeError):
        raise ConfigurationError("Cannot read local environment configuration") from None
    return {**local, **os.environ}


def _validated(model: type[BaseModel], values: dict[str, str | None]) -> BaseModel:
    fields = {name: values[name.upper()] for name in model.model_fields if name.upper() in values}
    if model is WeatherSettings and "weather_fallback_providers" in fields:
        fields["weather_fallback_providers"] = tuple(
            s.strip() for s in (fields["weather_fallback_providers"] or "").split(",") if s.strip()
        )
    try:
        return model.model_validate(fields)
    except ValidationError as exc:
        names = sorted(
            {
                str(error["loc"][0]).upper() if error["loc"] else model.__name__
                for error in exc.errors(include_input=False)
            }
        )
        raise ConfigurationError("Invalid or missing configuration: " + ", ".join(names)) from None


def load_database_settings(env_file: Path = BACKEND_ROOT / ".env") -> DatabaseSettings:
    values = environment(env_file)
    # Process/local URI wins; the external file is read only when it is needed.
    if not values.get("MONGODB_URI") and values.get("MONGODB_ENV_FILE"):
        path = Path(values["MONGODB_ENV_FILE"])
        if not path.is_absolute():
            path = env_file.parent / path
        try:
            if not path.is_file():
                raise OSError
            private = dotenv_values(path, interpolate=False)
        except (OSError, UnicodeDecodeError):
            raise ConfigurationError("Cannot read MONGODB_ENV_FILE") from None
        values["MONGODB_URI"] = private.get("MONGODB_URI")
    return _validated(DatabaseSettings, values)


def load_weather_settings(env_file: Path = BACKEND_ROOT / ".env") -> WeatherSettings:
    return _validated(WeatherSettings, environment(env_file))
