from __future__ import annotations

import logging
import sqlite3
from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from tibiawikisql.models import Achievement, Charm, Creature, House, Item, Npc

if TYPE_CHECKING:
    from collections.abc import Generator

logging.basicConfig(level=logging.DEBUG)

sql_logger = logging.getLogger("sqlite3")

app = FastAPI(
    title="TibiaWikiSQL",
)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "title": exc.__class__.__name__,
            "message": str(exc),
        },
    )

def get_db_connection() -> Generator[sqlite3.Connection]:
    conn = sqlite3.connect("tibiawiki.db")
    conn.set_trace_callback(sql_logger.info)
    try:
        yield conn
    finally:
        conn.close()

Conn = Annotated[sqlite3.Connection, Depends(get_db_connection)]

@app.get("/healthcheck", tags=["General"])
def healthcheck() -> bool:
    return True


@app.get("/achievements/{title}")
def get_achievement(
        conn: Conn,
        title: str,
) -> Achievement | None:
    return Achievement.get_one_by_field(conn, "title", title)

@app.get("/charms/{title}")
def get_charm(
        conn: Conn,
        title: str,
) -> Charm | None:
    return Charm.get_one_by_field(conn, "title", title)

@app.get("/creatures/{title}")
def get_creature(
        conn: Conn,
        title: str,
) -> Creature | None:
    return Creature.get_one_by_field(conn, "title", title)

@app.get("/houses/{title}")
def get_house(
        conn: Conn,
        title: str,
) -> House | None:
    return House.get_one_by_field(conn, "title", title)


@app.get("/items/{title}")
def get_item(
        conn: Conn,
        title: str,
) -> Item | None:
    return Item.get_one_by_field(conn, "title", title)

@app.get("/npcs/{title}")
def get_npc(
        conn: Conn,
        title: str,
) -> Npc | None:
    return Npc.get_one_by_field(conn, "title", title)
