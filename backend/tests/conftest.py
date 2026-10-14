"""Deterministic tests cannot read real credentials or contact external services."""

import socket
from pathlib import Path

import dns.asyncresolver
import pytest

from app import settings

LOOPBACK = {"127.0.0.1", "::1", "localhost"}


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch, tmp_path):
    for name in tuple(settings.os.environ):
        if name.startswith(("MONGODB_", "WEATHER_", "NASA_POWER_", "OPEN_METEO_")):
            monkeypatch.delenv(name)

    read_env = settings.dotenv_values

    def isolated_file(path, **kwargs):
        if not Path(path).resolve().is_relative_to(tmp_path.resolve()):
            raise AssertionError("Tests may only read temporary synthetic environment files")
        return read_env(path, **kwargs)

    def deny_network(*args, **kwargs):
        raise AssertionError("External network is forbidden in deterministic tests")

    real_connect = socket.socket.connect
    real_getaddrinfo = socket.getaddrinfo

    # Windows event loops build their self-pipe from a loopback socket pair.
    def loopback_connect(sock, address):
        if isinstance(address, tuple) and address[0] in LOOPBACK:
            return real_connect(sock, address)
        deny_network()

    def loopback_getaddrinfo(host, *args, **kwargs):
        if host is None or host in LOOPBACK:
            return real_getaddrinfo(host, *args, **kwargs)
        deny_network()

    monkeypatch.setattr(settings, "dotenv_values", isolated_file)
    monkeypatch.setattr(socket.socket, "connect", loopback_connect)
    monkeypatch.setattr(socket, "getaddrinfo", loopback_getaddrinfo)
    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(dns.asyncresolver, "resolve", deny_network)


@pytest.fixture
def db_settings():
    return settings.DatabaseSettings(
        mongodb_uri="mongodb+srv://synthetic:encoded%40secret@cluster.example.mongodb.net/",
        mongodb_timeout_ms=100,
    )
