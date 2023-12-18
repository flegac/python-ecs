from typing import Self, Iterable

from pydantic import Field

from easy_lib.my_model import MyModel
from easy_lib.timing import time_func
from python_ecs.component import Component
from python_ecs.types import EntityId


class UpdateStatus(MyModel):
    birth: list[Component | list[Component]] = Field(default_factory=list)
    death: set[EntityId] = Field(default_factory=set)

    @staticmethod
    def add(items: list[Component | list[Component]]):
        return UpdateStatus(birth=items)

    @staticmethod
    def remove(ids: EntityId | Iterable[EntityId]):
        if isinstance(ids, EntityId):
            ids = [ids]
        return UpdateStatus(death=set(ids))

    @time_func
    def load(self, other: Self):
        if other is None:
            return
        self.death.update(other.death)
        self.birth.extend(other.birth)
