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


from tibiawikisql.models.base import WithStatus, WithVersion
from tibiawikisql.api import WikiEntry


class House(WikiEntry, WithVersion, WithStatus):
    """Represents a house or guildhall."""

    house_id: int
    """The house's id on tibia.com."""
    name: str
    """The name of the house."""
    is_guildhall: bool
    """Whether the house is a guildhall or not."""
    city: str
    """The city where the house is located."""
    street: str | None
    """The name of the street where the house is located."""
    location: str | None
    """A brief description of where the house is."""
    beds: int
    """The maximum number of beds the house can have."""
    rent: int
    """The monthly rent of the house."""
    size: int
    """The number of tiles (SQM) of the house."""
    rooms: int | None
    """The number of rooms the house has."""
    floors: int | None
    """The number of floors the house has."""
    x: int | None
    """The x coordinate of the house."""
    y: int | None
    """The y coordinate of the house."""
    z: int | None
    """The z coordinate of the house."""
