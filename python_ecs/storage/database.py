from typing import Type, override

from easy_kit.timing import time_func
from python_ecs.component import Component
from python_ecs.component_set import ComponentSet, flatten_components
from python_ecs.signature import Signature
from python_ecs.storage.database_api import DatabaseAPI
from python_ecs.storage.demography import Demography
from python_ecs.storage.id_generator import IdGenerator
from python_ecs.storage.index import Index
from python_ecs.types import EntityId

EID_GEN = IdGenerator()


class Database(DatabaseAPI):
    def __init__(self):
        self._entities: set[EntityId] = set()
        self.tables: dict[Type[Component | Signature], Index] = {}
        self.dirty: Demography = Demography()

    @override
    def find_any[T: Component](self, what: Type[T], having: list[Type[Component]] = None) -> T:
        table = self.get_table(what)
        eids = table.entities
        for _ in having or []:
            eids.intersection_update(self.get_table(_).entities)

        if eids:
            eid = next(iter(eids))
            return table.read(eid)

    @override
    def entities(self):
        return self._entities

    @override
    def create_all(self, items: list[ComponentSet]):
        items = list(map(flatten_components, items))
        for components in items:
            eid = EID_GEN.new_id()
            for _ in components:
                _.eid = eid

        self.dirty.with_birth(items)

    @override
    def destroy_all(self, items: Component | Signature | list[Component | Signature]):
        self.dirty.with_death(items)

    @override
    def get_table[T:Component | Signature](self, ttype: Type[T]) -> Index[T]:
        if ttype not in self.tables:
            self.tables[ttype] = Index(ttype=ttype)
        return self.tables[ttype]

    @time_func
    def union_entities(self, signature: list[Type[Component]]):
        res = set()
        for _ in signature:
            res.update(self.tables[_].by_entity.keys())
        return res

    @time_func
    def intersect_entities(self, signature: list[Type[Component]]):
        if not signature:
            return set()
        first = signature[0]
        if first not in self.tables:
            return set()

        res = self.tables[first].entities
        for _ in signature[1:]:
            res.intersection_update(self.tables[_].entities)
            if not res:
                return res
        return res

    # -----------------------------------------------------------------------------

    @time_func
    def update_demography(self, status: Demography):
        death = status.death

        self._entities.difference_update(death)
        for table in self.tables.values():
            table.destroy_all(death)

        birth = filter(None, status.birth)
        for components in birth:
            self._entities.add(components[0].eid)
            for c in components:
                if c is None:
                    continue
                c.db = self
                ctype = c.type_id
                self.get_table(ctype).create(c)
