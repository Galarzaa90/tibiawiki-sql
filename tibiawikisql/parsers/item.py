import re
from typing import Any, ClassVar

from tibiawikisql.api import Article
from tibiawikisql.models.item import Item, ItemAttribute, ItemStoreOffer
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser
from tibiawikisql.schema import ItemTable
from tibiawikisql.utils import (
    clean_links,
    clean_question_mark,
    client_color_to_rgb,
    find_templates,
    parse_boolean,
    parse_float,
    parse_integer,
    parse_sounds,
    strip_code,
)


class ItemParser(BaseParser):
    """Parses items and objects."""
    model = Item
    table = ItemTable
    template_name = "Infobox_Object"
    attribute_map: ClassVar = {
        "name": AttributeParser.required("name"),
        "actual_name": AttributeParser.optional("actualname"),
        "plural": AttributeParser.optional("plural", clean_question_mark),
        "article": AttributeParser.optional("article"),
        "is_marketable": AttributeParser.optional("marketable", parse_boolean, False),
        "is_stackable": AttributeParser.optional("stackable", parse_boolean, False),
        "is_pickupable": AttributeParser.optional("pickupable", parse_boolean, False),
        "is_immobile": AttributeParser.optional("immobile", parse_boolean, False),
        "value_sell": AttributeParser.optional("npcvalue", parse_integer),
        "value_buy": AttributeParser.optional("npcprice", parse_integer),
        "weight": AttributeParser.optional("weight", parse_float),
        "flavor_text": AttributeParser.optional("flavortext"),
        "item_class": AttributeParser.optional("objectclass"),
        "item_type": AttributeParser.optional("primarytype"),
        "type_secondary": AttributeParser.optional("secondarytype"),
        "light_color": AttributeParser.optional("lightcolor", lambda x: client_color_to_rgb(parse_integer(x))),
        "light_radius": AttributeParser.optional("lightradius", parse_integer),
        "version": AttributeParser.optional("implemented"),
        "client_id": AttributeParser.optional("itemid", parse_integer),
        "status": AttributeParser.status(),
    }

    item_attributes: ClassVar = {
        "required_level": "levelrequired",
        "required_vocation": "vocrequired",
        "attack": "attack",
        "attack_extra": "atk_mod",
        "defense": "defense",
        "defense_modifier": "defensemod",
        "armor": "armor",
        "hands": "hands",
        "imbuement_slots": "imbueslots",
        "imbuements": "imbuements",
        "hit_chance": "hit_chance",
        "hit_chance_extra": "hit_mod",
        "range": "range",
        "damage_type": "damagetype",
        "damage_range": "damagerange",
        "mana_cost": "manacost",
        "required_magic_level": "mlrequired",
        "words": "words",
        "critical_hit_extra_chance": "crithit_ch",
        "critical_hit_extra_damage": "critextra_dmg",
        "hp_leech_chance": "hpleech_ch",
        "hp_leech_amount": "hpleech_am",
        "mana_leech_chance": "manaleech_ch",
        "mana_leech_amount": "manaleech_am",
        "volume": "volume",
        "charges": "charges",
        "food_time": "regenseconds",
        "duration": "duration",
        "attack_fire": "fire_attack",
        "attack_energy": "energy_attack",
        "attack_ice": "ice_attack",
        "attack_earth": "earth_attack",
        "attack_death": "death_attack",
        "weapon_type": "weapontype",
        "destructible": "destructible",
        "holds_liquid": "holdsliquid",
        "is_hangable": "hangable",
        "is_writable": "writable",
        "is_rewritable": "rewritable",
        "writable_chars": "writechars",
        "is_consumable": "consumable",
        "fansite": "fansite",
        "blocks_projectiles": "unshootable",
        "blocks_path": "blockspath",
        "is_walkable": "walkable",
        "tile_friction": "walkingspeed",
        "map_color": "mapcolor",
        "upgrade_classification": "upgradeclass",
        "is_rotatable": "rotatable",
        "augments": "augments",
        "elemental_bond": "elementalbond",
        "mantra": "mantra",
        "base_power": "basepower",
        "cooldown": "cooldown",
        "wrappable": "wrappable",
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        row["attributes"] = []
        for name, attribute in cls.item_attributes.items():
            if attribute in row["_raw_attributes"] and row["_raw_attributes"][attribute]:
                row["attributes"].append(ItemAttribute(
                    name=name,
                    value=clean_links(row["_raw_attributes"][attribute]),
                ))
        cls.parse_item_attributes(row)
        cls.parse_resistances(row)
        cls.parse_sounds(row)
        cls.parse_store_value(row)
        return row

    @classmethod
    def parse_item_attributes(cls, row: dict[str, Any]):
        raw_attributes = row["_raw_attributes"]
        attributes = row["attributes"]
        if "attrib" not in raw_attributes:
            return
        attribs = raw_attributes["attrib"].split(",")
        for attr in attribs:
            attr = attr.strip()
            if "perfect shot" in attr.lower():
                numbers = re.findall(r"(\d+)", attr)
                if len(numbers) == 2:
                    attributes.extend([
                        ItemAttribute(name="perfect_shot", value=f"+{numbers[0]}"),
                        ItemAttribute(name="perfect_shot_range", value=numbers[1]),
                    ])
                    continue
            if "damage reflection" in attr.lower():
                value = parse_integer(attr)
                attributes.append(
                    ItemAttribute(name="damage_reflection", value=str(value))
                )
            if "magic shield capacity" in attr.lower():
                numbers = re.findall(r"(\d+)", attr)
                if len(numbers) == 2:
                    attributes.extend([
                        ItemAttribute(name="magic_shield_capacity", value=f"+{numbers[0]}"),
                        ItemAttribute(name="magic_shield_capacity%", value=f"{numbers[1]}%"),
                    ])
                    continue
            magic_level = re.fullmatch(
                r"(?:(.+?)\s+)?magic level\s+([+\-]?\d+)", attr, re.IGNORECASE
            )
            if magic_level:
                prefix = magic_level.group(1)
                attribute = "magic_level"
                if prefix:
                    normalized_prefix = prefix.strip().lower().replace(" ", "_")
                    attribute = f"magic_level_{normalized_prefix}"
                attributes.append(
                    ItemAttribute(name=attribute, value=magic_level.group(2))
                )
                continue
            m = re.search(r"([\s\w]+)\s([+\-\d]+)", attr)
            if m:
                attribute = (
                    m.group(1).lower().replace("fighting", "").strip().replace(" ", "_")
                )
                value = m.group(2)
                attributes.append(ItemAttribute(name=attribute.lower(), value=value))
            if "regeneration" in attr:
                attributes.append(ItemAttribute(name="regeneration", value="faster regeneration"))

    @classmethod
    def parse_resistances(cls, row):
        raw_attributes = row["_raw_attributes"]
        attributes = row["attributes"]
        if "resist" not in raw_attributes:
            return
        resistances = raw_attributes["resist"].split(",")
        for element in resistances:
            element = element.strip()
            m = re.search(r"([a-zA-Z0-9_ ]+) +(-?\+?\d+)%", element)
            if not m:
                continue
            element = m.group(1).strip().lower().replace(" ", "_")
            attribute = f"resistance_{element}"
            try:
                value = int(m.group(2))
            except ValueError:
                value = 0
            attributes.append(ItemAttribute(name=attribute, value=str(value)))

    @classmethod
    def parse_sounds(cls, row):
        if "sounds" not in row["_raw_attributes"]:
            return
        row["sounds"] = parse_sounds(row["_raw_attributes"]["sounds"])

    @classmethod
    def parse_store_value(cls, row):
        if "storevalue" not in row["_raw_attributes"]:
            return
        templates = find_templates(row["_raw_attributes"]["storevalue"], "Store Product", recursive=True)
        row["store_offers"] = []
        for template in templates:
            price = int(strip_code(template.get(1, 0)))
            currency = strip_code(template.get(2, "Tibia Coin"))
            amount = int(strip_code(template.get("amount", 1)))
            row["store_offers"].append(
                ItemStoreOffer(price=price, currency=currency, amount=amount),
            )
