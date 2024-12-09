import asyncio
import functools
import logging

import niquests
import youtube_search

from exse import constants

log = logging.getLogger(__file__)


async def fetch_video_data(idx: str, api_key: str):
    async with niquests.AsyncSession() as session:
        resp = await session.post(
            constants.YT_PLAYER_URL.update_query(key=api_key),
            headers=constants.YT_PLAYER_HEADERS,
            json=dict(videoId=idx, context=dict(client=constants.YT_CLIENT)),
        )
        return resp.json()


def find_optimal_stream(vid_data: dict) -> dict:
    for f in vid_data["streamingData"]["adaptiveFormats"]:
        if f["itag"] != 140:
            continue
        return f


async def iter_stream_from_id(
    idx: str,
    start: int = 0,
    end: int | None = None,
    chunk_size: int = constants.YT_STREAM_HTTP_CHUNK_SIZE,
):
    # TODO: implement server-side caching?
    headers = {
        "User-Agent": "Lavf/58.76.100",
        "Range": f"bytes={start}-{end or ''}",
    }

    vid_data = await fetch_video_data(idx, constants.YT_API_KEY)
    opt_stream = find_optimal_stream(vid_data)
    opt_stream_url = opt_stream["url"]

    async with niquests.AsyncSession() as session:
        resp = await session.get(opt_stream_url, headers=headers, stream=True)
        if resp.status_code == 416:
            raise ValueError(f"Out of range: {start=}")

        assert resp.status_code == 206
        contents = await resp.iter_content(chunk_size)

        try:
            async for chunk in contents:
                yield chunk
        except GeneratorExit:
            await resp.close()


async def iter_stream_from_query(query: str, *args, **kwargs):
    loop = asyncio.get_running_loop()
    res = await loop.run_in_executor(
        None, functools.partial(youtube_search.YoutubeSearch, query, max_results=1)
    )
    res = res.to_dict()
    async for chunk in iter_stream_from_id(res[0]["id"], *args, **kwargs):
        yield chunk
