import logging

import uvicorn
from fastapi import FastAPI
from reactpy import component, html
from reactpy.backend.fastapi import configure

import exse

log = logging.getLogger(__file__)


@component
def App():
    return html.h1("Hello, world!")


async def main():
    import os

    app = FastAPI()
    configure(app, App)
    uconf = uvicorn.Config(app, port=8080, log_level=os.environ["UVICORN_LOG_LEVEL"])
    server = uvicorn.Server(uconf)
    await server.serve()
