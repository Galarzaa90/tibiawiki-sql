#  Copyright (c) 2025.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import sqlite3
from typing import Any

import tibiawikisql.schema
from tibiawikisql.api import Article
from tibiawikisql.models.outfit import Outfit, OutfitQuest
from tibiawikisql.parsers import BaseParser
from tibiawikisql.parsers.base import AttributeParser, M
from tibiawikisql.parsers.quest import parse_links
from tibiawikisql.utils import parse_boolean, parse_integer


class OutfitParser(BaseParser):  # noqa: D101
    model = Outfit
    table = tibiawikisql.schema.OutfitTable
    template_name = "Infobox_Outfit"
    attribute_map = {
        "name": AttributeParser.required("name"),
        "outfit_type": AttributeParser.required("primarytype"),
        "is_premium": AttributeParser.optional("premium", parse_boolean, False),
        "is_tournament": AttributeParser.optional("tournament", parse_boolean, False),
        "is_bought": AttributeParser.optional("bought", parse_boolean, False),
        "full_price": AttributeParser.optional("fulloutfitprice", parse_integer),
        "achievement": AttributeParser.optional("achievement"),
        "status": AttributeParser.status(),
        "version": AttributeParser.version(),
    }

    @classmethod
    def parse_attributes(cls, article: Article) -> dict[str, Any]:
        row = super().parse_attributes(article)
        if not row:
            return row
        raw_attributes = row["_raw_attributes"]
        article_id = row["article_id"]
        title = row["title"]
        row["quests"] = []
        if "outfit" in raw_attributes:
            quests = parse_links(raw_attributes["outfit"])
            for quest in quests:
                row["quests"].append(OutfitQuest(
                    outfit_id=article_id,
                    quest_title=quest.strip(),
                    type="outfit",
                    outfit_title=title,
                ))
        if "addons" in raw_attributes:
            quests = parse_links(raw_attributes["addons"])
            for quest in quests:
                row["quests"].append(OutfitQuest(
                    outfit_id=article_id,
                    quest_title=quest.strip(),
                    type="addons",
                    outfit_title=title,
                ))
        return row

    @classmethod
    def insert(cls, cursor: sqlite3.Cursor | sqlite3.Connection, model: Outfit) -> None:
        super().insert(cursor, model)
        for quest in model.quests:
            tibiawikisql.schema.OutfitQuestTable.insert(cursor, **quest.model_dump())


