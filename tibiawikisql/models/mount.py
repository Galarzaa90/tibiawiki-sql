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

from tibiawikisql.api import WikiEntry
from tibiawikisql.models.base import WithStatus, WithVersion



class Mount(WikiEntry, WithStatus, WithVersion):
    """Represents a Mount."""

    name: str
    """The name of the mount."""
    speed: int
    """The speed given by the mount."""
    taming_method: str
    """A brief description on how the mount is obtained."""
    is_buyable: bool
    """Whether the mount can be bought from the store or not."""
    price: int | None
    """The price in Tibia coins to buy the mount."""
    achievement: str | None
    """The achievement obtained for obtaining this mount."""
    light_color: int | None
    """The color of the light emitted by this mount in RGB, if any."""
    light_radius: int | None
    """The radius of the light emitted by this mount, if any."""
    image: bytes | None = None
    """The NPC's image in bytes."""

