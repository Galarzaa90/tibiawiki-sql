from __future__ import annotations

import logging
import sqlite3
from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, FastAPI

from tibiawikisql.models import Achievement, Charm, Creature, Npc

if TYPE_CHECKING:
    from collections.abc import Generator

logging.basicConfig(level=logging.DEBUG)

sql_logger = logging.getLogger("sqlite3")

app = FastAPI(
    title="TibiaWikiSQL",
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
    achievement = Achievement.get_by_field(conn, "title", title)
    return achievement

@app.get("/charms/{title}")
def get_charm(
        conn: Conn,
        title: str,
) -> Charm | None:
    charm = Charm.get_by_field(conn, "title", title)
    return charm

@app.get("/creatures/{title}")
def get_creature(
        conn: Conn,
        title: str,
) -> Creature | None:
    creature = Creature.get_by_field(conn, "title", title)
    return creature



@app.get("/npcs/{title}")
def get_npc(
        conn: Conn,
        title: str,
) -> Npc | None:
    npc = Npc.get_by_field(conn, "title", title)
    return npc
