import argparse
import asyncio
import logging
import sys

from exse import util

log = logging.getLogger(__file__)


async def cmd_daemon(args):
    from exse.yt import daemon

    await daemon.main()


async def cmd_query(args):
    from exse import yt

    stream = yt.iter_stream_from_query(args.query)

    async for chunk in stream:
        sys.stdout.buffer.write(chunk)


async def cmd_play(args):
    from exse import yt

    stream = yt.iter_stream_from_id(args.video_id)

    async for chunk in stream:
        sys.stdout.buffer.write(chunk)


parser = argparse.ArgumentParser(description="Exse's YT backend.")

subparsers = parser.add_subparsers()

parser_daemon = subparsers.add_parser(
    "daemon", help="Serve a websocket server to talk to Exse's YT backend."
)
parser_daemon.set_defaults(func=cmd_daemon)

parser_query = subparsers.add_parser("query", help="TODO")
parser_query.add_argument("query")
parser_query.set_defaults(func=cmd_query)

parser_play = subparsers.add_parser("play", help="TODO")
parser_play.add_argument("video_id")
parser_play.set_defaults(func=cmd_play)


def main():
    LOG_LEVEL = "INFO"
    parser.add_argument(
        "-L",
        "--log-level",
        help="Set log level. Options: DEBUG, INFO (default), CRITICAL, ERROR",
        type=str,
        default="INFO",
    )
    args = parser.parse_args()
    LOG_LEVEL = args.log_level

    logging.basicConfig(util.default_logging_config(LOG_LEVEL))

    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
