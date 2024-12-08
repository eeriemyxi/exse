import logging

from reactpy import component, html, run

import exse

log = logging.getLogger(__file__)


@component
def App():
    return html.h1("Hello, world!")


def main():
    run(App)
