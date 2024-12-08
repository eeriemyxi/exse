import asyncio
import configparser
import functools
import io
import logging
import pathlib
import sys

import aiofiles
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from exse import util, yt

log = logging.getLogger(__file__)
config = configparser.ConfigParser()
config.read(util.get_config_location(sys.platform) / "config.ini")

SP_CLIENT_ID = config.get("spotify", "CLIENT_ID")
SP_CLIENT_SECRET = config.get("spotify", "CLIENT_SECRET")
SP_REDIRECT_URI = config.get("spotify", "REDIRECT_URI")

CACHE_DIR = pathlib.Path(config.get("general", "CACHE_DIR"))


async def setup_spotify():
    loop = asyncio.get_running_loop()
    sp = await loop.run_in_executor(
        None,
        functools.partial(
            spotipy.Spotify,
            auth_manager=SpotifyOAuth(
                client_id=SP_CLIENT_ID,
                client_secret=SP_CLIENT_SECRET,
                redirect_uri=SP_REDIRECT_URI,
                scope="user-library-read",
            ),
        ),
    )
    return sp


def cache_file(title):
    return (CACHE_DIR / title).with_suffix(".m4a")


async def readable_cache_for_song(title):
    try:
        async with aiofiles.open(cache_file(title), "rb") as file:
            return await file.read()
    except FileNotFoundError:
        return b""


async def streamify(data, chunk_size):
    idata = io.BytesIO(data)
    while True:
        chunk = idata.read(chunk_size)
        if not chunk:
            return
        await asyncio.sleep(0)
        yield chunk


async def stream_track(track):
    ftitle = ", ".join(a["name"] for a in track["artists"]) + " - " + track["name"]
    chunk_size = yt.HTTP_CHUNK_SIZE
    read_yet = 0

    rcache = await readable_cache_for_song(ftitle)
    wcache = await aiofiles.open(cache_file(ftitle), "wb")

    stream = streamify(rcache, chunk_size)

    while True:
        try:
            chunk = await anext(stream)
        except StopAsyncIteration:
            stream = yt.iter_stream_from_query(ftitle, read_yet)
            try:
                chunk = await anext(stream)
            except (StopAsyncIteration, ValueError):
                break

        yield chunk
        await wcache.write(chunk)
        read_yet += len(chunk)

    await wcache.close()


async def stream_track_from_id(idx: str):
    loop = asyncio.get_running_loop()

    spotify = await setup_spotify()
    track = await loop.run_in_executor(None, functools.partial(spotify.track, idx))

    async for chunk in stream_track(track):
        yield chunk
