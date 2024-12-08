import argparse
import logging
import sys

from exse import util

log = logging.getLogger(__file__)


def cmd_query(args):
    from exse import yt

    stream = yt.iter_stream_from_query(args.query)
    _ = next(stream)

    for chunk in stream:
        sys.stdout.buffer.write(chunk)


def cmd_play(args):
    from exse import yt

    stream = yt.iter_stream_from_id(args.video_id)
    _ = next(stream)

    for chunk in stream:
        sys.stdout.buffer.write(chunk)


parser = argparse.ArgumentParser(description="TODO")

subparsers = parser.add_subparsers()

parser_stream = subparsers.add_parser("query", help="TODO")
parser_stream.add_argument("query")
parser_stream.set_defaults(func=cmd_query)

parser_stream = subparsers.add_parser("play", help="TODO")
parser_stream.add_argument("video_id")
parser_stream.set_defaults(func=cmd_play)


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

    args.func(args)


if __name__ == "__main__":
    main()
