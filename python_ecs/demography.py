from typing import Self, Iterable

from easy_kit.timing import time_func
from pydantic import Field

from easy_config.my_model import MyModel
from python_ecs.component import ComponentSet, Component, Signature
from python_ecs.types import EntityId


class Demography(MyModel):
    birth: list[list[Component]] = Field(default_factory=list)
    death: set[EntityId] = Field(default_factory=set)

    def with_birth(self, items: list[ComponentSet]):
        def convert(item: ComponentSet):
            if isinstance(item, Component):
                return [item]
            if isinstance(item, Signature):
                return item.to_components()
            return item

        self.birth.extend(map(convert, items))
        return self

    def with_death(self, ids: EntityId | Iterable[EntityId]):
        if isinstance(ids, int):
            ids = [ids]
        self.death.update(ids)
        return self

    @time_func
    def load(self, other: Self):
        if other is None:
            return self
        self.death.update(other.death)
        self.birth.extend(other.birth)
        return self
