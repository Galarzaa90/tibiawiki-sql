from __future__ import annotations

import logging
import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from starlette.requests import Request

from tibiawikisql.models import Npc

logging.basicConfig(level=logging.DEBUG)

sql_logger = logging.getLogger("sqlite3")

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = app.state.conn = sqlite3.connect("tibiawiki.db")
    conn.set_trace_callback(sql_logger.info)
    yield
    conn.close()

app = FastAPI(
    title="TibiaWikiSQL",
    lifespan=lifespan,
)


def get_db_connection(request: Request) -> sqlite3.Connection:
    return request.app.state.conn

Conn = Annotated[sqlite3.Connection, Depends(get_db_connection)]

@app.get("/healthcheck", tags=["General"])
async def healthcheck() -> bool:
    return True


@app.get("/npcs/{title}")
async def get_npc(
        conn: Conn,
        title: str,
):
    npc = Npc.get_by_field(conn, "title", title)
    return npc
