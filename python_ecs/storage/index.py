from dataclasses import field
from typing import Type, Iterable

from easy_config.my_model import MyModel
from python_ecs.component import Component
from python_ecs.signature import Signature
from python_ecs.types import EntityId


class Index[T: Signature | Component](MyModel):
    ttype: Type[T]
    by_entity: dict[EntityId, T] = field(default_factory=dict)

    @property
    def entities(self):
        return set(self.by_entity.keys())

    def list_all(self, eids: Iterable[EntityId] = None):
        if eids is not None:
            return list(map(self.read, eids))
        return list(self.by_entity.values())

    def create(self, item: T):
        self.by_entity[item.eid] = item

    def read(self, eid: EntityId):
        return self.by_entity.get(eid, None)

    def read_any(self):
        return next(iter(self.by_entity.values()))

    def destroy(self, eid: EntityId):
        return self.by_entity.pop(eid, None)

    def destroy_all(self, eids: Iterable[EntityId]):
        for _ in eids:
            self.destroy(_)
