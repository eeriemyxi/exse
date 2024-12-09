import os
import pathlib


def is_connected():
    import socket

    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False


def default_logging_config(log_level):
    return dict(
        level=log_level.upper(),
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def get_config_location(platform: str):
    if platform == "linux":
        assert "HOME" in os.environ, "Please set $HOME env var."
        return pathlib.Path(os.environ["HOME"]) / ".config/exse"
    if platform == "win32":
        assert "APP_DATA" in os.environ
        return pathlib.Path(os.environ["APP_DATA"]) / "exse"
