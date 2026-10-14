import pytest
from pydantic import ValidationError

from app.settings import (
    ConfigurationError,
    DatabaseSettings,
    WeatherSettings,
    load_database_settings,
    load_weather_settings,
)

URI = "mongodb+srv://synthetic:encoded%40secret@cluster.example.mongodb.net/"


def test_environment_precedence_and_external_file_scope(tmp_path, monkeypatch):
    private = tmp_path / "private.env"
    private.write_text(f"MONGODB_URI={URI}\nMONGODB_DATABASE=ignored_private_name\n")
    local = tmp_path / ".env"
    local.write_text("MONGODB_ENV_FILE=private.env\nMONGODB_DATABASE=local_name\n")
    result = load_database_settings(local)
    assert result.mongodb_uri.get_secret_value() == URI
    assert result.mongodb_database == "local_name"
    local_uri = URI.replace("synthetic", "local")
    local.write_text(f"MONGODB_ENV_FILE=missing.env\nMONGODB_URI={local_uri}\n")
    assert load_database_settings(local).mongodb_uri.get_secret_value() == local_uri
    monkeypatch.setenv("MONGODB_URI", URI)
    monkeypatch.setenv("MONGODB_DATABASE", "process_name")
    assert load_database_settings(local).mongodb_uri.get_secret_value() == URI
    assert load_database_settings(local).mongodb_database == "process_name"


def test_interpolation_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("UNRELATED_SECRET", "do-not-expand")
    uri = URI.replace("encoded%40secret", "${UNRELATED_SECRET}")
    local = tmp_path / ".env"
    local.write_text(f"MONGODB_URI='{uri}'\n")
    assert load_database_settings(local).mongodb_uri.get_secret_value() == uri


@pytest.mark.parametrize("query", [
    "tls=false", "ssl=false", "tlsInsecure=true", "tlsAllowInvalidCertificates=true",
    "tlsAllowInvalidHostnames=true", "tls=false&tls=true", "TLS=false&tls=true",
    "tlsInsecure=true&tlsInsecure=false", "retryWrites=true;tls=false",
])
def test_unsafe_tls_options_rejected(query):
    with pytest.raises(ValidationError, match="TLS-verified"):
        DatabaseSettings(mongodb_uri=URI + "?" + query)


@pytest.mark.parametrize("uri", [
    "mongodb://synthetic:secret@localhost/", URI.replace("mongodb.net", "evil.example"),
    URI.replace("encoded%40secret", ""), URI.replace("encoded%40secret", "raw@secret"),
    URI.replace("encoded%40secret", "bad%zz"), URI + "#fragment",
    URI.replace(".net/", ".net:27017/"), URI.replace("encoded%40secret", "has space"),
])
def test_invalid_uri_is_safe(uri):
    with pytest.raises(ValidationError) as error:
        DatabaseSettings(mongodb_uri=uri)
    assert uri not in str(error.value)
    assert "encoded%40secret" not in str(error.value)


@pytest.mark.parametrize("content", ["", "MONGODB_URI=private-value", "MONGODB_ENV_FILE=gone"])
def test_missing_or_invalid_configuration_is_safe(tmp_path, content):
    local = tmp_path / ".env"
    local.write_text(content)
    with pytest.raises(ConfigurationError) as error:
        load_database_settings(local)
    assert "private-value" not in str(error.value)
    assert str(tmp_path) not in str(error.value)


@pytest.mark.parametrize("external", [False, True])
def test_invalid_encoding_is_safe(tmp_path, external):
    local = tmp_path / ".env"
    if external:
        local.write_text("MONGODB_ENV_FILE=private.env")
        (tmp_path / "private.env").write_bytes(b"\xffprivate-value")
    else:
        local.write_bytes(b"\xffprivate-value")
    with pytest.raises(ConfigurationError) as error:
        load_database_settings(local)
    assert "private-value" not in str(error.value)


@pytest.mark.parametrize("field,value", [
    ("mongodb_timeout_ms", 99), ("mongodb_timeout_ms", 30001),
    ("mongodb_database", "unsafe.name"), ("mongodb_database", "a" * 64),
])
def test_database_limits(field, value):
    with pytest.raises(ValidationError):
        DatabaseSettings(mongodb_uri=URI, **{field: value})


def test_secret_repr_and_provider_safety(tmp_path):
    assert "encoded%40secret" not in repr(DatabaseSettings(mongodb_uri=URI))
    assert WeatherSettings().provider_order == ("nasa_power",)
    with pytest.raises(ValidationError, match="non-commercial"):
        WeatherSettings(weather_fallback_enabled=True)
    with pytest.raises(ValidationError):
        WeatherSettings(nasa_power_base_url="https://evil.example")
    local = tmp_path / ".env"
    local.write_text(
        "WEATHER_FALLBACK_ENABLED=true\nOPEN_METEO_NONCOMMERCIAL_USE=true\n"
        "WEATHER_FALLBACK_PROVIDERS=open_meteo,nasa_power,open_meteo\n"
    )
    assert load_weather_settings(local).provider_order == ("nasa_power", "open_meteo")


@pytest.mark.parametrize("uri", [
    "mongodb://127.0.0.1:27017/", "mongodb://localhost:27017", "mongodb://[::1]:27017/",
])
def test_loopback_uri_needs_explicit_local_development(uri):
    with pytest.raises(ValidationError):
        DatabaseSettings(mongodb_uri=uri)
    assert DatabaseSettings(mongodb_uri=uri, mongodb_local_development=True).is_local


@pytest.mark.parametrize("uri", [
    "mongodb://10.0.0.5:27017/", "mongodb://evil.example/", "mongodb://127.0.0.1,evil.example/",
    "mongodb+srv://127.0.0.1/",
])
def test_local_development_still_rejects_non_loopback_hosts(uri):
    with pytest.raises(ValidationError):
        DatabaseSettings(mongodb_uri=uri, mongodb_local_development=True)


def test_atlas_uri_is_not_local_even_with_flag():
    assert DatabaseSettings(mongodb_uri=URI, mongodb_local_development=True).is_local is False
