import argparse
import asyncio
import logging
import sys

from exse import util
from exse.yt.__main__ import parser as yt_parser

LOG_LEVEL = "INFO"
log = logging.getLogger(__file__)


async def cmd_daemon(args):
    from exse import daemon

    await daemon.main()


async def cmd_stream(args):
    import exse

    spotify = await exse.setup_spotify()
    track = spotify.track(args.track_id)

    async for chunk in exse.stream_track(track):
        sys.stdout.buffer.write(chunk)


async def cmd_load_web(args):
    import os

    os.environ["UVICORN_LOG_LEVEL"] = LOG_LEVEL
    from exse import web

    await web.main()


async def cmd_load_tui(args):
    from exse import tui

    await tui.main()


async def _show_version():
    import importlib.metadata

    print(importlib.metadata.version("exse"))


parser = argparse.ArgumentParser(description="TODO")
parser.add_argument(
    "-L",
    "--log-level",
    help="Set log level. Options: debug, info (default), critical, error",
    type=str,
    default="info",
)
parser.add_argument(
    "-v",
    "--version",
    help="See current version.",
    action="store_true",
)
subparsers = parser.add_subparsers()

parser_daemon = subparsers.add_parser(
    "daemon",
    help="Serve a websocket server to talk to Exse.",
)
parser_daemon.set_defaults(func=cmd_daemon)

parser_stream = subparsers.add_parser("stream", help="Stream audio to stdout.")
parser_stream.add_argument("track_id")
parser_stream.set_defaults(func=cmd_stream)

parser_tui = subparsers.add_parser("tui", help="Open the TUI interface.")
parser_tui.set_defaults(func=cmd_load_tui)

parser_web = subparsers.add_parser("web", help="Open the web interface.")
parser_web.set_defaults(func=cmd_load_web)

parser_yt = subparsers.add_parser(
    "yt", help="TODO", parents=[yt_parser], conflict_handler="resolve"
)

args = parser.parse_args()
LOG_LEVEL = args.log_level.casefold()

logging.basicConfig(**util.default_logging_config(LOG_LEVEL))

if args.version:
    _show_version()
    exit()

if not hasattr(args, "func"):
    parser.print_help()
    exit(1)

try:
    asyncio.run(args.func(args))
except KeyboardInterrupt:
    pass


def main():
    pass
