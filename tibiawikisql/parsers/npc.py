import re
import sqlite3
from typing import Any, ClassVar

import tibiawikisql.schema
from tibiawikisql.api import Article
from tibiawikisql.models.npc import Npc
from tibiawikisql.models.npc import (
    NpcBuyOffer,
    NpcDestination,
    NpcSellOffer,
    NpcSpell,
)
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.utils import clean_links, convert_tibiawiki_position, find_template, strip_code

price_to_template = re.compile(r"{{(?:NPC List\s*|Price to (?:Buy|Sell))\s*([^}]+)}}")
npc_offers = re.compile(r"\|([^|:\[]+)(?::\s?(\d+))?(?:\s?\[\[([^\]]+))?")

teaches_template = re.compile(r"{{Teaches\s*(?:\|name=([^|]+))?([^}]+)}}")
spells_pattern = re.compile(r"\|([^|]+)")

trades_sell_template = re.compile(r"{{Trades/Sells\s*(?:\|note=([^|]+))?([^}]+)}}")
npc_trades = re.compile(r"\|([^|,\[]+)(?:,\s?([+-]?\d+))?(?:\s?\[\[([^\]]+))?")

ilink_pattern = re.compile(r"{{Ilink\|([^}]+)}}")


class NpcParser(BaseParser):
    """Parser for NPCs."""

    table = tibiawikisql.schema.NpcTable
    model = Npc
    template_name = "Infobox_NPC"
    attribute_map: ClassVar = {
        "name": AttributeParser(lambda x: x.get("actualname") or x.get("name")),
        "gender": AttributeParser.optional("gender"),
        "location": AttributeParser.optional("location", clean_links),
        "subarea": AttributeParser.optional("subarea"),
        "city": AttributeParser.required("city"),
        "x": AttributeParser.optional("posx", convert_tibiawiki_position),
        "y": AttributeParser.optional("posy", convert_tibiawiki_position),
        "z": AttributeParser.optional("posz", int),
        "version": AttributeParser.optional("implemented"),
        "status": AttributeParser.status(),
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        raw_attributes = row["_raw_attributes"]
        cls._parse_jobs(row)
        cls._parse_races(row)
        if "buys" in raw_attributes and article.title != "Minzy":
            cls._parse_buy_offers(row)
        if "sells" in raw_attributes and article.title != "Minzy":
            cls._parse_sell_offers(row)
            cls._parse_spells(row)
        row["destinations"] = []
        destinations = []
        if "notes" in raw_attributes and "{{Transport" in raw_attributes["notes"]:
            destinations.extend(cls.parse_destinations(raw_attributes["notes"]))
        if "sells" in raw_attributes and "{{Transport" in raw_attributes["sells"]:
            destinations.extend(cls.parse_destinations(raw_attributes["sells"]))
        for destination, price, notes in destinations:
            destination.strip()
            notes = clean_links(notes.strip())
            price = int(price)
            if not notes:
                notes = None
            row["destinations"].append(NpcDestination(
                npc_id=row["article_id"],
                name=destination,
                price=price,
                notes=notes,
            ))
        return row


    # region Auxiliary Methods

    @classmethod
    def _parse_jobs(cls, row):
        raw_attributes = row["_raw_attributes"]
        jobs = row["jobs"] = []
        if "job" in raw_attributes:
            jobs.append(raw_attributes["job"])
        for i in range(2, 7):
            key = f"job{i}"
            if key in raw_attributes:
                jobs.append(clean_links(raw_attributes[key]))

    @classmethod
    def _parse_races(cls, row):
        raw_attributes = row["_raw_attributes"]
        races = row["races"] = []
        if "race" in raw_attributes:
            races.append(raw_attributes["race"])
        for i in range(2, 7):
            key = f"race{i}"
            if key in raw_attributes:
                races.append(clean_links(raw_attributes[key]))

    @classmethod
    def _parse_buy_offers(cls, row):
        raw_attributes = row["_raw_attributes"]
        article_id = row["article_id"]
        buy_offers = row["buy_offers"] = []
        buy_items = cls.parse_item_offers(raw_attributes["buys"])
        for item, price, currency in buy_items:
            # Some items have extra requirements, separated with ;, so we remove them
            item = item.split(";")[0]
            if not currency.strip():
                currency = "Gold Coin"
            value = None
            if "type=" in item:
                continue
            if price.strip():
                value = int(price)
            buy_offers.append(NpcBuyOffer(
                item_title=item.strip(),
                currency_title=currency,
                value=value,
                npc_id=article_id,
            ))

    @classmethod
    def _parse_sell_offers(cls, row):
        raw_attributes = row["_raw_attributes"]
        article_id = row["article_id"]
        sell_offers = row["sell_offers"] = []
        sell_items = cls.parse_item_offers(raw_attributes["sells"])
        for item, price, currency in sell_items:
            # Some items have extra requirements, separated with ;, so we remove them
            item = item.split(";")[0]
            if not currency.strip():
                currency = "Gold Coin"
            value = None
            if price.strip():
                value = int(price)
            sell_offers.append(NpcSellOffer(
                item_title=item.strip(),
                currency_title=currency,
                value=value,
                npc_id=article_id,
            ))
        # Items traded by npcs (these have a different template)
        trade_items = cls.parse_item_trades(raw_attributes["sells"])
        for item, price, currency in trade_items:
            item = item.split(";")[0]
            value = None
            if price.strip():
                value = abs(int(price))
            if not currency.strip():
                currency = "Gold Coin"
            sell_offers.append(NpcSellOffer(
                item_title=item.strip(),
                currency_title=currency,
                value=value,
                npc_id=article_id,
            ))

    @classmethod
    def _parse_spells(cls, row):
        raw_attributes = row["_raw_attributes"]
        article_id = row["article_id"]
        npc_name = row["name"]
        jobs = "".join(row["jobs"]).lower()
        teaches = row["teaches"] = []
        spell_list = cls.parse_spells(raw_attributes["sells"])
        for group, spells in spell_list:
            for spell in spells:
                spell = spell.strip()
                knight = "knight" in group.lower() or npc_name == "Eliza"
                paladin = "paladin" in group.lower() or npc_name == "Ursula" or npc_name == "Eliza"
                druid = "druid" in group.lower() or npc_name == "Elathriel" or npc_name == "Eliza"
                sorcerer = "sorcerer" in group.lower() or npc_name == "Eliza"
                monk = "monk" in group.lower()
                if not (knight or paladin or druid or sorcerer or monk):
                    knight = "knight" in jobs
                    paladin = "paladin" in jobs
                    druid = "druid" in jobs
                    sorcerer = "sorcerer" in jobs
                    monk = "monk" in jobs
                exists = False
                for j, s in enumerate(teaches):
                    # Spell was already in list, so we update vocations
                    if s.spell_title == spell:
                        teaches[j] = NpcSpell(
                            npc_id=article_id,
                            spell_title=spell,
                            knight=knight or s.knight,
                            paladin=paladin or s.paladin,
                            druid=druid or s.druid,
                            sorcerer=sorcerer or s.sorcerer,
                            monk=monk or s.monk,
                        )
                        exists = True
                        break
                if not exists:
                    teaches.append(NpcSpell(
                        npc_id=article_id,
                        spell_title=spell,
                        knight=knight,
                        paladin=paladin,
                        druid=druid,
                        sorcerer=sorcerer,
                        monk=monk,
                    ))

    @classmethod
    def parse_destinations(cls, value):
        """Parse an NPC destinations into a list of tuples.

        The tuple contains the  destination's name, price and notes.
        Price and notes may not be present.

        Parameters
        ----------
        value: :class:`str`
            A string containing destinations.

        Returns
        -------
        list(:class:`tuple`)
            A list of tuples containing the parsed destinations.

        """
        template = find_template(value, "Transport", partial=True)
        if not template:
            return []
        result = []
        for param in template.params:
            if param.showkey:
                continue
            data, *notes = strip_code(param).split(";", 1)
            notes = notes[0] if notes else ""
            destination, price = data.split(",")
            result.append((destination, price, notes))
        return result

    @classmethod
    def parse_item_offers(cls, value):
        """Parse NPC item offers into a list of tuples.

        The tuple contains the item's name, price and currency.
        Price and currency may not be present.

        Parameters
        ----------
        value: :class:`str`
            The string  containing NPC offers.

        Returns
        -------
        list(:class:`tuple`)
            A list of tuples containing the parsed offers.

        """
        match = price_to_template.search(value)
        if match:
            return npc_offers.findall(match.group(1))
        return []

    @classmethod
    def parse_item_trades(cls, value):
        """Parse an NPC item trades into a list of tuples.

        The tuple contains the item's name, price and currency.
        Price and currency may not be present.

        Parameters
        ----------
        value: :class:`str`
            A string containing item trades.

        Returns
        -------
        list(:class:`tuple`)
            A list of tuples containing the parsed offers.

        """
        result = []
        value = cls.replace_ilinks(value)
        for note, trades in trades_sell_template.findall(value):
            result.extend(npc_trades.findall(trades))
        return result

    @classmethod
    def parse_spells(cls, value):
        """Parse an NPC's teacheable spells.

        Parameters
        ----------
        value: :class:`str`
            A string containing teachable spells.

        Returns
        -------
        A list of spells grouped by vocation.

        """
        result = []
        for name, spell_list in teaches_template.findall(value):
            spells = spells_pattern.findall(spell_list)
            spells = [s.strip() for s in spells]
            result.append((name, spells))
        return result

    @classmethod
    def replace_ilinks(cls, value):
        """Replace the ILink template with a regular link.

        Parameters
        ----------
        value: :class:`str`
            A string containing ILink templates.

        Returns
        -------
        :class:`str`
            The string with regular links instead of ILink templates.

        """
        return ilink_pattern.sub(r"[[\g<1>]]", value)

    # endregion
