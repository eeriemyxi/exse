import asyncio
import json
import logging

from websockets.server import serve

import exse

log = logging.getLogger(__name__)


async def daemon(websocket):
    async for message in websocket:
        response = json.loads(message)
        if response["from"] == "id":
            stream = exse.stream_track_from_id(response["id"])

        async for chunk in stream:
            await websocket.send(chunk)


async def main():
    async with serve(daemon, "localhost", 8765):
        await asyncio.get_running_loop().create_future()
