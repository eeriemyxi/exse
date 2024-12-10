import asyncio
import json
import logging

from websockets.server import serve

import exse

log = logging.getLogger(__name__)

spotify = exse.setup_spotify()


async def daemon(websocket):
    async for message in websocket:
        response = json.loads(message)
        if response["from"] == "id":
            log.info("[spotify] Streaming from id")
            stream = exse.stream_track_from_id(spotify, response["id"])

        if response["from"] == "track":
            log.info("[spotify] Streaming from track")
            stream = exse.stream_track_from_track(spotify, response["track"])

        async for chunk in stream:
            log.info("[spotify] Sending a chunk (%s size).", len(chunk))
            await websocket.send(chunk)


async def main():
    async with serve(daemon, "0.0.0.0", 8765):
        await asyncio.get_running_loop().create_future()
