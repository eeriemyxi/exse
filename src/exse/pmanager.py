from __future__ import annotations

import asyncio
import functools
import logging
import pathlib
import pickle
import uuid
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
        self.pending_writes = set()

        if should_load_cache:
            self.playlists = self.load_cache(self.cache_path)

    def update_event_loop(self):
        self.loop = asyncio.get_running_loop()

    def set_spotify(self, spotify):
        self.spotify = spotify

    def load_cache(self, cache_path: pathlib.Path):
        data = {}
        if not cache_path.exists():
            log.debug(f"{cache_path=} doesn't exist. Returning {data=}")
            return data

        with open(cache_path, "rb") as cache:
            try:
                self._cache_read = True
                data = pickle.loads(cache.read())
            except EOFError as e:
                log.error(e)
                log.debug(f"{cache_path=} is corrupted or empty. Returning {data=}.")
                return data
            else:
                log.debug(f"Successfully loaded {cache_path=}.")
                self._cache_read = True
                return data

    async def update_cache(self):
        read_id = uuid.uuid4()
        self.pending_writes.add(read_id)

        log.debug("[%s] Trying to save playlist cache at %s", read_id, self.cache_path)
        async with aiofiles.open(self.cache_path, "wb") as cache:
            data = await self.loop.run_in_executor(
                None, functools.partial(pickle.dumps, self.playlists)
            )
            log.debug("[%s] Saving playlist cache at %s", read_id, self.cache_path)
            await cache.write(data)

        self.pending_writes.remove(read_id)

    async def close(self):
        log.debug("Initiating plugin manager's closing process.")
        while len(self.pending_writes) > 0:
            log.debug("Waiting for pending writes to finish.")
            asyncio.sleep(0.1)
        log.debug("Closing plugin manager.")
        return

    async def getch_batch_for(self, playlist_id: str, offset: int, name: str = None):
        if (
            playlist_id in self.playlists
            and offset in self.playlists[playlist_id].batches
        ):
            log.debug(f"Fetching {playlist_id=} {name=} {offset=} from cache")
            data = self.playlists[playlist_id].batches[offset]
            return data

        await self.fetch_batch_for(playlist_id, offset, name)

    async def fetch_batch_for(
        self, playlist_id: str, offset: int, name: str | None = None
    ):
        log.debug(f"Fetching {playlist_id=} {offset=} {name=}")

        if playlist_id == "__saved__":
            tracks = await self.loop.run_in_executor(
                None,
                functools.partial(
                    self.spotify.current_user_saved_tracks, offset=offset, limit=50
                ),
            )
            tracks = tracks["items"]
            name = "Liked Songs"
        else:
            tracks = await self.loop.run_in_executor(
                None,
                functools.partial(
                    self.spotify.playlist_tracks, playlist_id, offset=offset, limit=100
                ),
            )

        if not tracks:
            return None

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
