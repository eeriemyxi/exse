import asyncio
import logging

from websockets.server import serve

log = logging.getLogger(__name__)


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def main():
    async with serve(echo, "localhost", 8765):
        log.debug("Daemon is serving.")
        await asyncio.get_running_loop().create_future()  # run forever
