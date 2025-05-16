from __future__ import annotations

import logging
import sqlite3
from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from tibiawikisql.models import Achievement, Charm, Creature, House, Imbuement, Item, Key, Mount, Npc, Outfit, Quest, \
    Spell, \
    Update, \
    World

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
    return Achievement.get_by_title(conn, title)


@app.get("/charms/{title}")
def get_charm(
        conn: Conn,
        title: str,
) -> Charm | None:
    return Charm.get_by_title(conn, title)


@app.get("/creatures/{title}")
def get_creature(
        conn: Conn,
        title: str,
) -> Creature | None:
    return Creature.get_by_title(conn, title)


@app.get("/houses/{title}")
def get_house(
        conn: Conn,
        title: str,
) -> House | None:
    return House.get_by_title(conn, title)

@app.get("/imbuements/{title}")
def get_imbuement(
        conn: Conn,
        title: str,
) -> Imbuement | None:
    return Imbuement.get_by_title(conn, title)


@app.get("/items/{title}")
def get_item(
        conn: Conn,
        title: str,
) -> Item | None:
    return Item.get_by_title(conn, title)

@app.get("/keys/{title}")
def get_key(
        conn: Conn,
        title: str,
) -> Key | None:
    return Key.get_by_title(conn, title)


@app.get("/mounts/{title}")
def get_mount(
        conn: Conn,
        title: str,
) -> Mount | None:
    return Mount.get_by_title(conn, title)

@app.get("/npcs/{title}")
def get_npc(
        conn: Conn,
        title: str,
) -> Npc | None:
    return Npc.get_by_title(conn, title)

@app.get("/outfits/{title}")
def get_outfit(
        conn: Conn,
        title: str,
) -> Outfit | None:
    return Outfit.get_by_title(conn, title)

@app.get("/quests/{title}")
def get_quest(
        conn: Conn,
        title: str,
) -> Quest | None:
    return Quest.get_by_title(conn, title)


@app.get("/spells/{title}")
def get_spell(
        conn: Conn,
        title: str,
) -> Spell | None:
    return Spell.get_by_title(conn, title)


@app.get("/updates/byVersion/{version}")
def get_update_by_version(
        conn: Conn,
        version: str,
) -> Update | None:
    return Update.get_one_by_field(conn, "version", version)


@app.get("/updates/{title:path}")
def get_update(
        conn: Conn,
        title: str,
) -> Update | None:
    return Update.get_by_title(conn, title)


@app.get("/worlds/{title}")
def get_world(
        conn: Conn,
        title: str,
) -> World | None:
    return World.get_by_title(conn, title)
