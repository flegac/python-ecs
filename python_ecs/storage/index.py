from typing import Type

from python_ecs.component import Signature
from python_ecs.types import EntityId


class Index[T: Signature]:
    def __init__(self, stype: Type[T]):
        self.stype = stype
        self.items: dict[EntityId, T] = dict()

    def find(self, eid: EntityId):
        return self.items.get(eid, None)

    def pop(self, eid: EntityId):
        return self.items.pop(eid, None)
