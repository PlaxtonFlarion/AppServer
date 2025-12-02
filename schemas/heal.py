#  _   _            _
# | | | | ___  __ _| |
# | |_| |/ _ \/ _` | |
# |  _  |  __/ (_| | |
# |_| |_|\___|\__,_|_|
#

import typing
from pydantic import BaseModel


class Locator(BaseModel):
    by: str
    value: str


class ElementNode(BaseModel):
    id: typing.Optional[str]
    text: typing.Optional[str]
    content_desc: typing.Optional[str]
    resource_id: typing.Optional[str]
    bounds: list[int]
    class_name: str


class HealRequest(BaseModel):
    app_id: str
    page_id: str
    old_locator: Locator
    elements: list[ElementNode]
    screenshot: typing.Optional[str]
    context: typing.Optional[dict[str, typing.Any]]


class HealResponse(BaseModel):
    healed: bool
    confidence: float
    new_locator: typing.Optional[dict]
    details: dict


if __name__ == '__main__':
    pass


