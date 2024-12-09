import asyncio
import json
import logging

from websockets.server import serve

import exse.yt

log = logging.getLogger(__name__)


async def daemon(websocket):
    async for message in websocket:
        response = json.loads(message)
        if response["from"] == "id":
            stream = exse.yt.iter_stream_from_id(response["id"])
        elif response["from"] == "query":
            stream = exse.yt.iter_stream_from_query(response["query"])

        async for chunk in stream:
            await websocket.send(chunk)


async def main():
    async with serve(daemon, "localhost", 8765):
        await asyncio.get_running_loop().create_future()
