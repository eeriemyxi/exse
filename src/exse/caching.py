from __future__ import annotations

import asyncio
import functools
import logging
import pathlib
import pickle
from collections import OrderedDict
from dataclasses import dataclass

import aiofiles

log = logging.getLogger(__name__)


@dataclass
class PlaylistBatch:
    playlist: Playlist
    offset: int
    tracks: list[dict]


@dataclass
class Playlist:
    batches: OrderedDict[int, PlaylistBatch]
    name: str
    id: str


class PlaylistManager:
    DEFAULT_CACHING_INTERVAL = 50

    def __init__(self, cache_path: pathlib.Path, spotify=None, should_load_cache=True):
        self.cache_path = cache_path
        self.spotify = spotify
        self.playlists: dict[str, Playlist] = {}

        self.loop = asyncio.get_running_loop()
        self.should_use_cache = False

        if should_load_cache:
            self.playlists = self.load_cache(self.cache_path)
            # self.should_use_cache = True

    def load_cache(self, cache_path: pathlib.Path):
        if not cache_path.exists():
            return dict
        with open(cache_path, "rb") as cache:
            return pickle.load(cache)

    async def _instantiate_caching(self, interval):
        while True:
            await self.update_cache()
            await asyncio.sleep(interval)

    async def start_caching(self):
        asyncio.create_task(self._instantiate_caching(self.DEFAULT_CACHING_INTERVAL))

    async def update_cache(self):
        async with aiofiles.open(self.cache_path, "wb") as cache:
            data = await self.loop.run_in_executor(
                None, functools.partial(pickle.dumps, self.playlists)
            )
            log.debug("Saving playlist cache at %s", self.cache_path)
            await cache.write(data)

    async def getch_batch_for(self, playlist_id: str, name: str, offset: int):
        if (
            playlist_id in self.playlists
            and offset in self.playlists[playlist_id].batches
        ):
            log.info(f"Fetching {playlist_id=} {name=} {offset=} from cache")
            return self.playlists[playlist_id].batches[offset]
        return await self.fetch_batch_for(playlist_id, name, offset)

    async def fetch_batch_for(self, playlist_id: str, name: str, offset: int):
        tracks = await self.loop.run_in_executor(
            None,
            functools.partial(self.spotify.playlist_tracks, playlist_id, offset=offset),
        )

        playlist = self.playlists.get(
            playlist_id,
            Playlist(batches=OrderedDict(), name=name, id=playlist_id),
        )
        self.playlists[playlist_id] = playlist

        playlist.batches[offset] = PlaylistBatch(
            playlist=playlist, offset=offset, tracks=tracks
        )

        await self.update_cache()

        return playlist.batches[offset]

    async def get_playlist(self, playlist_id: str):
        return self.playlists[playlist_id]
