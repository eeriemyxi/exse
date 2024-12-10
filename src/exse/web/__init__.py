from nicegui import ui, element
import logging
import exse
import functools
from exse import constants, pmanager, util

log = logging.getLogger(__name__)


class SongEntry(element.Element, component="song_entry.js"):
    def __init__(self, title: str, artist: str, on_click):
        super().__init__()
        self._props["title"] = title
        self._props["artist"] = artist
        self.on("click", on_click)


class AudioPlayer(element.Element, component="player.js"):
    def __init__(self):
        super().__init__()
        self.audio_player_id = None

    def set_audio_player(self, id: int):
        self.audio_player_id = id

    def play(self, song_id):
        log.debug(f"Playing {song_id=}")
        self.run_method("play", f"c{self.audio_player_id}", song_id)


@ui.refreshable
async def playlist_tracks(audio_player, tracks):
    if not tracks:
        ui.label("No tracks.")
        return

    for track in tracks:
        track_artists_str = ", ".join(a["name"] for a in track["track"]["artists"])
        track_name = track["track"]["name"]
        SongEntry(
            track_name,
            track_artists_str,
            functools.partial(audio_player.play, track["track"]),
        )


spotify = exse.setup_spotify() if util.is_connected() else None
pman = pmanager.PlaylistManager(constants.PLAYLIST_CACHE_FILE, spotify)


@ui.page("/")
async def main_interface():
    ui.dark_mode().enable()
    ui.colors(**constants.GRUVBOX_COLORS)

    audio_player = AudioPlayer()

    batch = await pman.getch_batch_for("__saved__", 0)

    with (
        ui.column(align_items="center")
        .props("flat bordered")
        .classes("justify-center w-full items-stretch")
        .style("padding: 5px; gap: 1px;")
    ):
        await playlist_tracks(audio_player, batch.tracks)

    with (
        ui.footer()
        .style("background-color: #282828;")
        .classes("justify-center w-full items-stretch")
    ):
        base_audio = ui.audio("").classes("w-full")
        audio_player.set_audio_player(base_audio.id)


async def main():
    ui.run(host="0.0.0.0")
