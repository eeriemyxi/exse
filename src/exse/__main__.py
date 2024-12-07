import argparse
import configparser
import io
import pathlib
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import exse
from exse import util, yt


def cmd_play(args):
    spotify = exse.setup_spotify()
    track = spotify.track(args.track_id)

    for chunk in exse.stream_track(track):
        try:
            sys.stdout.buffer.write(chunk)
        except BrokenPipeError:
            return


def cmd_load_ui(args):
    from exse import ui

    ui.main()


parser = argparse.ArgumentParser(description="TODO")

subparsers = parser.add_subparsers()

parser_play = subparsers.add_parser("play", help="TODO")
parser_play.add_argument("track_id")
parser_play.set_defaults(func=cmd_play)

parser_stream = subparsers.add_parser("ui", help="TODO")
parser_stream.set_defaults(func=cmd_load_ui)

args = parser.parse_args()

if not hasattr(args, "func"):
    parser.print_help()
    exit(1)
try:
    args.func(args)
except KeyboardInterrupt:
    pass


def main():
    pass
