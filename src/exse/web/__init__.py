import functools
import logging
from collections import namedtuple
from dataclasses import dataclass

from nicegui import element, ui

import exse
from exse import constants, pmanager, util

log = logging.getLogger(__name__)
logging.getLogger("spotipy").setLevel("INFO")


@dataclass
class CurrentPlaylist:
    id: str = None
    batches: list = None
    offset: int = None
    displaying_more: bool = False


@dataclass
class State:
    batches: list = None
    current_playlist: CurrentPlaylist = None
    audio_player: object = None


class SongEntry(element.Element, component="song_entry.js"):
    def __init__(self, title: str, artist: str, on_click):
        super().__init__()
        self._props["title"] = title
        self._props["artist"] = artist
        self.on("click", on_click)


class PlaylistEntry(element.Element, component="playlist_entry.js"):
    def __init__(self, title: str, on_click):
        super().__init__()
        self._props["title"] = title
        self.on("click", on_click)


class AudioPlayer(element.Element, component="player.js"):
    def __init__(self):
        super().__init__()
        self._props["host"] = "192.168.29.35"
        self._props["port"] = 8765
        self.audio_player_id = None

    def set_audio_player(self, id: int):
        self.audio_player_id = id

    def play(self, track):
        log.debug(f"Playing {track['name']=}")
        self.run_method("play", f"c{self.audio_player_id}", track)


async def should_display_more_songs(pman, state, playlist_entries_el):
    try:
        if not await ui.run_javascript(
            "window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight"
        ):
            return
    except TimeoutError:
        log.debug("Got timeout error from should_display_more_songs")
        return

    if state.current_playlist.displaying_more:
        return

    state.current_playlist.displaying_more = True

    batch = await pman.getch_batch_for(state.current_playlist.id, state.current_playlist.offset)
    if not batch:
        log.debug(f"Not adding more songs because {batch=}")
        return

    state.current_playlist.offset += len(batch.tracks)
    state.current_playlist.batches.append(batch)

    for track in batch.tracks:
        await add_song_entry(state.audio_player, track, playlist_entries_el)

    state.current_playlist.displaying_more = False


async def add_song_entry(audio_player, track, to):
    track_artists_str = ", ".join(a["name"] for a in track["track"]["artists"])
    track_name = track["track"]["name"]
    entry = SongEntry(
        track_name,
        track_artists_str,
        functools.partial(audio_player.play, track["track"]),
    )
    entry.move(to)


@ui.refreshable
async def playlist_tracks(audio_player, batches, to):
    if not batches:
        ui.label("No tracks.")
        return

    for batch in batches:
        for track in batch.tracks:
            await add_song_entry(audio_player, track, to)


pman = pmanager.PlaylistManager(constants.PLAYLIST_CACHE_FILE, None)


@ui.page("/")
async def main_interface():
    ui.dark_mode().enable()
    ui.colors(**constants.GRUVBOX_COLORS)

    spotify = exse.setup_spotify() if util.is_connected() else None
    pman.update_event_loop()
    pman.set_spotify(spotify)

    state = State(
        current_playlist=CurrentPlaylist(batches=[], offset=50, displaying_more=False),
        audio_player=AudioPlayer(),
    )

    state.current_playlist.batches.append(
        await pman.fetch_batch_for("__saved__", 0)
        if util.is_connected()
        else await pman.getch_batch_for("__saved__", 0)
    )

    state.current_playlist.id = "__saved__"

    with (
        ui.column(align_items="center")
        .props("flat bordered")
        .classes("justify-center w-full items-stretch")
        .style("padding: 5px; gap: 1px;")
    ) as playlist_entries:
        await playlist_tracks(
            state.audio_player, state.current_playlist.batches, playlist_entries
        )

    with ui.left_drawer().style("background-color: #282828;"):
        with ui.column():
            if not util.is_connected():
                for pl in pman.playlists.values():
                    PlaylistEntry(pl.name, None)
            else:
                # TODO: manually add liked songs pl
                playlists = [
                    pl for pl in spotify.current_user_playlists()["items"] if pl
                ]
                for pl in playlists:
                    PlaylistEntry(pl["name"], None)

    with (
        ui.footer()
        .style("background-color: #282828;")
        .classes("justify-center w-full items-stretch")
    ):
        base_audio = ui.audio("").classes("w-full")
        state.audio_player.set_audio_player(base_audio.id)

    ui.timer(
        1,
        functools.partial(
            should_display_more_songs,
            pman,
            state,
            playlist_entries,
        ),
    )


async def main():
    ui.run(host="0.0.0.0")
