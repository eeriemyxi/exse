import argparse
import configparser
import io
import pathlib
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from exse import util, yt

config = configparser.ConfigParser()
config.read(util.get_config_location(sys.platform) / "config.ini")

SP_CLIENT_ID = config.get("spotify", "CLIENT_ID")
SP_CLIENT_SECRET = config.get("spotify", "CLIENT_SECRET")
SP_REDIRECT_URI = config.get("spotify", "REDIRECT_URI")

CACHE_DIR = pathlib.Path(config.get("general", "CACHE_DIR"))


def setup_spotify():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SP_CLIENT_ID,
            client_secret=SP_CLIENT_SECRET,
            redirect_uri=SP_REDIRECT_URI,
            scope="user-library-read",
        )
    )
    return sp


def cache_file(title):
    return (CACHE_DIR / title).with_suffix(".m4a")


def readable_cache_for_song(title):
    try:
        with open(cache_file(title), "rb") as file:
            return file.read()
    except FileNotFoundError:
        return b""


def streamify(data, chunk_size):
    idata = io.BytesIO(data)
    while True:
        chunk = idata.read(chunk_size)
        if not chunk:
            return
        yield chunk


def stream_track(track):
    ftitle = ", ".join(a["name"] for a in track["artists"]) + " - " + track["name"]
    chunk_size = yt.HTTP_CHUNK_SIZE
    read_yet = 0

    rcache = readable_cache_for_song(ftitle)
    wcache = open(cache_file(ftitle), "wb")

    stream = streamify(rcache, chunk_size)

    while True:
        try:
            chunk = next(stream)
        except StopIteration:
            stream = yt.iter_stream_from_query(ftitle, read_yet)
            try:
                chunk = next(stream)
            except (StopIteration, ValueError):
                break

        yield chunk
        wcache.write(chunk)
        read_yet += len(chunk)
        
    wcache.close()
