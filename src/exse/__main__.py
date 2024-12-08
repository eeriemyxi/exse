import argparse
import logging
import sys

from exse import util
from exse.yt.__main__ import parser as yt_parser

log = logging.getLogger(__file__)


def cmd_daemon(args):
    import asyncio

    from exse import daemon

    asyncio.run(daemon.main())


def cmd_stream(args):
    import exse

    spotify = exse.setup_spotify()
    track = spotify.track(args.track_id)

    for chunk in exse.stream_track(track):
        sys.stdout.buffer.write(chunk)


def cmd_load_web(args):
    from exse import web

    web.main()


def cmd_load_tui(args):
    from exse import tui

    tui.main()


def _show_version():
    import importlib.metadata

    print(importlib.metadata.version("exse"))


LOG_LEVEL = "INFO"

parser = argparse.ArgumentParser(description="TODO")
parser.add_argument(
    "-L",
    "--log-level",
    help="Set log level. Options: DEBUG, INFO (default), CRITICAL, ERROR",
    type=str,
    default="INFO",
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
    help="TODO",
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
LOG_LEVEL = args.log_level

logging.basicConfig(**util.default_logging_config(LOG_LEVEL))

if args.version:
    _show_version()
    exit()

if not hasattr(args, "func"):
    parser.print_help()
    exit(1)

try:
    args.func(args)
except KeyboardInterrupt:
    pass


def main():
    pass
