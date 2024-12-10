import asyncio
import functools
import io
import logging

import aiofiles
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from exse import constants, yt

log = logging.getLogger(__file__)


def setup_spotify():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=constants.SP_CLIENT_ID,
            client_secret=constants.SP_CLIENT_SECRET,
            redirect_uri=constants.SP_REDIRECT_URI,
            scope=("user-library-read", "playlist-read-private"),
        ),
    )
    return sp


def cache_file(title):
    return (constants.CACHE_DIR / title).with_suffix(".m4a")


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
    chunk_size = constants.YT_STREAM_HTTP_CHUNK_SIZE
    read_yet = 0

    rcache = await readable_cache_for_song(ftitle)
    wcache = await aiofiles.open(cache_file(ftitle), "wb")

    stream = streamify(rcache, chunk_size)

    while True:
        try:
            chunk = await anext(stream)
        except StopAsyncIteration:
            log.debug("Fetching stream data from YT.")
            if not util.is_connected():
                log.debug("Stopped fetching stream data due to no internet. Breaking.")
                break
            stream = yt.iter_stream_from_query(ftitle, read_yet)
            try:
                chunk = await anext(stream)
            except (StopAsyncIteration, ValueError):
                log.debug("Cannot fetch more streaming data. Breaking.")
                break

        yield chunk
        await wcache.write(chunk)
        read_yet += len(chunk)

    await wcache.close()


async def stream_track_from_id(spotify, idx: str):
    loop = asyncio.get_running_loop()

    track = await loop.run_in_executor(None, functools.partial(spotify.track, idx))

    async for chunk in stream_track(track):
        yield chunk


async def stream_track_from_track(spotify, track):
    async for chunk in stream_track(track):
        yield chunk
