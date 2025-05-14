from typing import Any, ClassVar

import tibiawikisql.schema
from tibiawikisql.api import Article
from tibiawikisql.models.npc import Npc, NpcDestination
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.utils import clean_links, convert_tibiawiki_position, find_template, strip_code


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

        row["destinations"] = []
        destinations = []
        if "notes" in raw_attributes and "{{Transport" in raw_attributes["notes"]:
            destinations.extend(cls._parse_destinations(raw_attributes["notes"]))
        for destination, price, notes in destinations:
            name = destination.strip()
            clean_notes = clean_links(notes.strip())
            if not notes:
                clean_notes = None
            row["destinations"].append(NpcDestination(
                name=name,
                price=price,
                notes=clean_notes,
            ))
        return row


    # region Auxiliary Methods

    @classmethod
    def _parse_jobs(cls, row: dict[str, Any]) -> None:
        """Read the possible multiple job parameters of an NPC's page and put them together in a list."""
        raw_attributes = row["_raw_attributes"]
        row["jobs"] = [
            clean_links(value)
            for key, value in raw_attributes.items()
            if key.startswith("job")
        ]

    @classmethod
    def _parse_races(cls, row: dict[str, Any]) -> None:
        """Read the possible multiple race parameters of an NPC's page and put them together in a list."""
        raw_attributes = row["_raw_attributes"]
        row["races"] = [
            clean_links(value)
            for key, value in raw_attributes.items()
            if key.startswith("race")
        ]


    @classmethod
    def _parse_destinations(cls, value: str) -> list[tuple[str, int, str]]:
        """Parse an NPC destinations into a list of tuples.

        The tuple contains the  destination's name, price and notes.
        Price and notes may not be present.

        Args:
            value: A string containing the Transport template with destinations.

        Returns:
            A list of tuples, where each element is the name of the destination, the price and additional notes.
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
            destination, price_str = data.split(",")
            try:
                price = int(price_str)
            except ValueError:
                price = 0
            result.append((destination, price, notes))
        return result

    # endregion
