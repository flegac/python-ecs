from typing import Type, Iterable

from pydantic import Field

from easy_lib.my_model import MyModel
from python_ecs.component import Component
from python_ecs.types import EntityId


class Components(MyModel):
    ctype: Type[Component]
    active: dict[EntityId, Component] = Field(default_factory=dict)
    inactive: dict[EntityId, Component] = Field(default_factory=dict)
    force_update: dict[EntityId, Component] = Field(default_factory=dict)

    def remove(self, eid: EntityId):
        self.active.pop(eid, None)
        self.inactive.pop(eid, None)

    def remove_all(self, eids: Iterable[EntityId]):
        for _ in eids:
            self.remove(_)

    def add(self, eid: EntityId, component: Component):
        component.eid = eid
        if component.is_active:
            self.active[eid] = component
        else:
            self.inactive[eid] = component
