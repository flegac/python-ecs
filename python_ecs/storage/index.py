from typing import Type

from python_ecs.component import Signature
from python_ecs.types import EntityId


class Index[T: Signature]:
    def __init__(self, stype: Type[T]):
        self.stype = stype
        self.systems: dict[Signature, list] = dict()
        self.items: dict[EntityId, T] = dict()
