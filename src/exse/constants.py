import configparser
import pathlib
import sys

import yarl

from exse import util

CONFIG_DIR = util.get_config_location(sys.platform)

config = configparser.ConfigParser()
config.read(CONFIG_DIR / "config.ini")

CACHE_DIR = pathlib.Path(config.get("general", "CACHE_DIR"))
PLAYLIST_CACHE_FILE = CONFIG_DIR / ".playlist_cache.bin"

SP_CLIENT_ID = config.get("spotify", "CLIENT_ID")
SP_CLIENT_SECRET = config.get("spotify", "CLIENT_SECRET")
SP_REDIRECT_URI = config.get("spotify", "REDIRECT_URI")

YT_API_KEY = config.get("youtube", "API_KEY")
YT_SEARCH_URL = yarl.URL("https://www.googleapis.com/youtube/v3/search")
YT_PLAYER_URL = yarl.URL("https://www.youtube.com/youtubei/v1/player")
YT_PLAYER_HEADERS = {
    "User-Agent": "com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip"
}
YT_CLIENT = {
    "clientName": "ANDROID",
    "clientVersion": "19.10.35",
    "androidSdkVersion": 30,
}
YT_STREAM_HTTP_CHUNK_SIZE = 1024 * 1024

GRUVBOX_COLORS = {
    "primary": "#427b58",
    "secondary": "#3c3836",
    "accent": "#d3869b",
    "dark": "#282828",
    "dark_page": "#282828",
    "positive": "#b5bd68",
    "negative": "#fb4934",
    "info": "#668cc0",
    "warning": "#f2c037",
}
