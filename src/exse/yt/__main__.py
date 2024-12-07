import argparse
import sys


def cmd_daemon(args):
    raise Exception("TODO")


def cmd_query(args):
    from exse import yt

    stream = yt.iter_stream_from_query(args.query)
    chunk_size = next(stream)

    for chunk in stream:
        sys.stdout.buffer.write(chunk)


def cmd_play(args):
    from exse import yt

    stream = yt.iter_stream_from_id(args.video_id)
    chunk_size = next(stream)

    for chunk in stream:
        sys.stdout.buffer.write(chunk)


parser = argparse.ArgumentParser(description="TODO")

subparsers = parser.add_subparsers()

parser_daemon = subparsers.add_parser(
    "daemon",
    help="TODO",
)
parser_daemon.set_defaults(func=cmd_daemon)

parser_stream = subparsers.add_parser("query", help="TODO")
parser_stream.add_argument("query")
parser_stream.set_defaults(func=cmd_query)

parser_stream = subparsers.add_parser("play", help="TODO")
parser_stream.add_argument("video_id")
parser_stream.set_defaults(func=cmd_play)

args = parser.parse_args()

if not hasattr(args, "func"):
    parser.print_help()
    exit(1)

args.func(args)


def main():
    pass
