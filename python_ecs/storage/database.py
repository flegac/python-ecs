from typing import Type, Iterable, Generator, Any

from easy_kit.timing import time_func

from python_ecs.component import Component, Signature, ComponentSet
from python_ecs.demography import Demography
from python_ecs.id_generator import IdGenerator
from python_ecs.storage.components import Components
from python_ecs.storage.index import Index
from python_ecs.types import EntityId

EID_GEN = IdGenerator()


class Database:
    def __init__(self):
        self.components: dict[Type[Component], Components] = {}
        self.indexes: dict[Type[Signature], Index] = {}
        self.ecs: Any = None
        self.dirty: Demography = Demography()

    def register(self, items: list[ComponentSet]):
        self.dirty.with_birth(items)

    def register_destroy(self, ids: EntityId | Iterable[EntityId]):
        self.dirty.with_death(ids)

    def get_index(self, sys: 'System'):
        if sys._signature not in self.indexes:
            self.indexes[sys._signature] = Index(sys._signature)
        return self.indexes[sys._signature]

    def iter[T:Component](self, ctype: Type[T]) -> Generator[T, Any, None]:
        if ctype not in self.components:
            return
        for _ in self.components[ctype].active.values():
            yield _

    def get_single[T:Component](self, ctype: Type[T]) -> T:
        return next(self.iter(ctype))

    @time_func
    def get[T: Component](self, key: Type[T], eid: EntityId) -> T | None:
        if key not in self.components:
            return None

        components = self.components[key]
        return components.active.get(eid)

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

    # -----------------------------------------------------------------------------

    @time_func
    def update_demography(self, status: Demography):
        self.destroy(status.death)
        return self.new_entities(status.birth)

    @time_func
    def new_entities(self, entities: list[list[Component]]):
        return [
            self.add(EntityId(EID_GEN.new_id()), components)
            for components in entities
            if components
        ]

    def add(self, eid: EntityId, components: list[Component]):
        for c in components:
            if c is None:
                continue
            c.ecs = self.ecs
            ctype = c.type_id
            if ctype not in self.components:
                self.components[ctype] = Components(ctype=ctype)
            self.components[ctype].add(eid, c)
        return eid

    @time_func
    def destroy(self, ids: Iterable[EntityId]):
        for c in self.components.values():
            c.remove_all(ids)
