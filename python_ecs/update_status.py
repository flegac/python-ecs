from typing import Self, Iterable

from pydantic import Field

from easy_config.my_model import MyModel
from easy_kit.timing import time_func
from python_ecs.component import ComponentSet, Component, Signature
from python_ecs.types import EntityId


class Demography(MyModel):
    birth: list[list[Component]] = Field(default_factory=list)
    death: set[EntityId] = Field(default_factory=set)

    @staticmethod
    def add(items: list[ComponentSet]):
        def convert(item: ComponentSet):
            if isinstance(item, Component):
                return [item]
            if isinstance(item, Signature):
                return item.to_components()
            return item

        items = list(map(convert, items))
        return Demography(birth=items)

    @staticmethod
    def remove(ids: EntityId | Iterable[EntityId]):
        if isinstance(ids, int):
            ids = [ids]
        return Demography(death=set(ids))

    @time_func
    def load(self, other: Self):
        if other is None:
            return self
        self.death.update(other.death)
        self.birth.extend(other.birth)
        return self
