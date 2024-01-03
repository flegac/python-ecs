import traceback
from dataclasses import dataclass
from typing import Iterable, Type

from loguru import logger
from pydantic import Field

from easy_lib.my_model import MyModel
from easy_lib.timing import time_func, timing
from python_ecs.component import Component, Signature
from python_ecs.storage.database import Database
from python_ecs.system import System
from python_ecs.types import EntityId
from python_ecs.update_status import Demography


@dataclass
class Entity:
    eid: EntityId
    ecs: 'ECS'

    def get[T: Component](self, key: Type[T]) -> T | None:
        return self.db.get(key, self.eid)

    def attach(self, item: Component):
        self.db.add(self.eid, item)
        for sys in self.systems:
            signature = sys._signature
            if signature is None:
                continue
            if issubclass(signature, Component) and type(item) is signature:
                sys.items[self.eid] = item
            if issubclass(signature, Signature):
                name = signature.field_mapping().get(type(item))
                if name:
                    setattr(sys.items[self.eid], name, item)

    @property
    def db(self):
        return self.ecs.db

    @property
    def systems(self):
        return self.ecs.systems


class ECS(MyModel):
    systems: list[System] = Field(default_factory=list)
    db: Database = Field(default_factory=Database)

    def find[T](self, key: Type[T]) -> T:
        with timing('ECS.find'):
            for _ in self.systems:
                if type(_) is key:
                    return _
            raise ValueError('not found')

    def entity(self, eid: EntityId):
        return Entity(eid=eid, ecs=self)

    def new_entity(self, item: list[Component] | Component | None):
        return self.create([item])

    @time_func
    def create(self, items: list[list[Component] | Component]):
        demography = Demography.add(items)
        self.db.new_entities(items)
        for sys in self.systems:
            sys.update_demography(demography)

    def destroy(self, ids: Iterable[EntityId]):
        status = Demography.remove(ids)
        for sys in self.systems:
            sys.update_demography(status)

        self.db.destroy(ids)

    @time_func
    def update(self):
        status = Demography()
        for sys in self.systems:
            try:
                status.load(sys.update(self.db))
            except Exception as e:
                logger.error(f'{sys.__class__.__name__}: {e}\n{traceback.format_exc()}')
        for sys in self.systems:
            sys.update_demography(status)
        self.db.update_demography(status)


# default simulator
sim = ECS()
