#  Copyright 2021 Allan Galarza
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

"""API that reads and parses information from `TibiaWiki <https://tibiawiki.fandom.com>`_."""

__author__ = "Allan Galarza"
__copyright__ = "Copyright 2021 Allan Galarza"

__license__ = "Apache 2.0"
__version__ = "6.2.0"

from tibiawikisql import models
from tibiawikisql.api import Article, Image, WikiClient, WikiEntry
