from typing import Self

from pydantic import Field

from easy_config.my_model import MyModel
from easy_kit.timing import time_func
from python_ecs.component import Component
from python_ecs.signature import Signature
from python_ecs.component_set import ComponentSet, flatten_components
from python_ecs.types import EntityId


class Demography(MyModel):
    birth: list[list[Component]] = Field(default_factory=list)
    death: set[EntityId] = Field(default_factory=set)

    def clear(self):
        self.birth.clear()
        self.death.clear()

    def with_birth(self, items: list[ComponentSet]):
        self.birth.extend(map(flatten_components, items))
        return self

    def with_death(self, items: Component | Signature | list[Component | Signature]):
        if isinstance(items, Component | Signature):
            items = [items]
        self.death.update([_.eid for _ in items])
        return self

    @time_func
    def load(self, other: Self):
        if other is None:
            return self
        self.death.update(other.death)
        self.birth.extend(other.birth)
        return self
