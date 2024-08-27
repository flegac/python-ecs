from typing import Type, Iterable, Generator, Any

from pydantic import Field

from easy_config.my_model import MyModel
from easy_kit.timing import time_func
from python_ecs.component import Component
from python_ecs.storage.components import Components
from python_ecs.id_generator import IdGenerator
from python_ecs.types import EntityId
from python_ecs.update_status import Demography

EID_GEN = IdGenerator()


class Database(MyModel):
    components: dict[Type[Component], Components] = Field(default_factory=dict)

    def iter[T](self, ctype: Type[T]) -> Generator[T, Any, None]:
        if ctype not in self.components:
            return
        for _ in self.components[ctype].active.values():
            yield _

    @time_func
    def update_demography(self, status: Demography):
        self.destroy(status.death)
        self.new_entities(status.birth)

    @time_func
    def new_entities(self, entities: list[list[Component] | Component]):
        for components in entities:
            if components:
                self.add(EntityId(EID_GEN.new_id()), components)

    def add(self, eid: EntityId, components: list[Component] | Component):
        if isinstance(components, Component):
            components = [components]
        for c in components:
            if c is None:
                continue
            ctype = c.type_id
            if ctype not in self.components:
                self.components[ctype] = Components(ctype=ctype)
            self.components[ctype].add(eid, c)

    @time_func
    def get[T: Component](self, key: Type[T], eid: EntityId) -> T | None:
        if key not in self.components:
            return None

        components = self.components[key]
        return components.active.get(eid)

    @time_func
    def destroy(self, ids: Iterable[EntityId]):
        for c in self.components.values():
            c.remove_all(ids)

    @property
    @time_func
    def entities(self) -> set[EntityId]:
        return set().union(*[set(_.active.keys()) for _ in self.components.values()])

    @time_func
    def union_entities(self, signature: list[Type[Component]]):
        res = set()
        for _ in signature:
            res.update(self.components[_].active.keys())
        return res

    @time_func
    def common_entities(self, signature: list[Type[Component]]):
        if not signature:
            return set()
        first = signature[0]
        if first not in self.components:
            return set()

        res = set(self.components[first].active.keys())
        for _ in signature[1:]:
            res.intersection_update(self.components[_].active.keys())
            if not res:
                return res
        return res
