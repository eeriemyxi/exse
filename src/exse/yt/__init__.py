import configparser
import logging
import sys

import requests
import yarl
import youtube_search

from exse import util

log = logging.getLogger(__file__)

config = configparser.ConfigParser()
config.read(util.get_config_location(sys.platform) / "config.ini")

YT_API_KEY = config.get("youtube", "API_KEY")
YT_SEARCH_URL = yarl.URL("https://www.googleapis.com/youtube/v3/search")
YT_PLAYER_URL = yarl.URL("https://www.youtube.com/youtubei/v1/player")
YT_PLAYER_HEADERS = {
    "User-Agent": "com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip"
}
CLIENT = {"clientName": "ANDROID", "clientVersion": "19.10.35", "androidSdkVersion": 30}

HTTP_CHUNK_SIZE = 1024 * 1024


def fetch_video_data(idx: str, api_key: str):
    resp = requests.post(
        YT_PLAYER_URL.update_query(key=api_key),
        headers=YT_PLAYER_HEADERS,
        json=dict(videoId=idx, context=dict(client=CLIENT)),
    )
    return resp.json()


def find_optimal_stream(vid_data: dict) -> dict:
    for f in vid_data["streamingData"]["adaptiveFormats"]:
        if f["itag"] != 140:
            continue
        return f


def iter_stream_from_id(
    idx: str, start: int = 0, end: int | None = None, chunk_size: int = HTTP_CHUNK_SIZE
):
    # TODO: implement server-side caching?
    headers = {
        "User-Agent": "Lavf/58.76.100",
        "Range": f"bytes={start}-{end or ''}",
    }

    vid_data = fetch_video_data(idx, YT_API_KEY)
    opt_stream = find_optimal_stream(vid_data)
    opt_stream_url = opt_stream["url"]

    resp = requests.get(opt_stream_url, headers=headers, stream=True)
    if resp.status_code == 416:
        raise ValueError(f"Out of range: {start=}")

    assert resp.status_code == 206

    try:
        yield from resp.iter_content(chunk_size)
    except GeneratorExit:
        resp.close()


def iter_stream_from_query(query: str, *args, **kwargs):
    res = youtube_search.YoutubeSearch(query, max_results=1).to_dict()
    yield from iter_stream_from_id(res[0]["id"], *args, **kwargs)
