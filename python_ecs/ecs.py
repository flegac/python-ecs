import traceback
from dataclasses import dataclass
from typing import Type

import time
from easy_kit.timing import time_func, timing
from loguru import logger

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
        self.db.add(self.eid, [item])
        for sys in self.systems:
            signature = sys._signature
            if signature is None:
                continue
            if issubclass(signature, Component) and type(item) is signature:
                # sys.items[self.eid] = item
                self.db.get_index(sys).items[self.eid] = item
            if issubclass(signature, Signature):
                name = signature.field_mapping().get(type(item))
                if name:
                    # data = sys.items.get(self.eid)
                    data = self.db.get_index(sys).items.get(self.eid)

                    if data:
                        setattr(self.db.get_index(sys).items[self.eid], name, item)

                        # setattr(sys.items[self.eid], name, item)

    @property
    def db(self):
        return self.ecs.db

    @property
    def systems(self):
        return self.ecs.systems


class ECS:
    def __init__(self, systems: list[System] = None):
        self.db = Database()
        self.db.ecs = self
        self.systems = systems or []
        self.last_updates = {}

    def iter[T:Component](self, ctype: Type[T]):
        return self.db.iter(ctype)

    def get_single[T:Component](self, ctype: Type[T]):
        return self.db.get_single(ctype)

    def find_sys[T](self, key: Type[T]) -> T:
        with timing('ECS.find'):
            for _ in self.systems:
                if type(_) is key:
                    return _
            raise ValueError('not found')

    def entity(self, eid: EntityId):
        return Entity(eid=eid, ecs=self)

    def retrieve(self, eid: EntityId, signature: Type[Signature]):
        return signature.cast([
            self.db.get(_, eid)
            for _ in signature.signature()
        ])

    @time_func
    def update(self):
        status = Demography()
        now = time.time()

        for sys in self.systems:
            sys_key = sys.__class__
            if sys_key not in self.last_updates:
                self.last_updates[sys_key] = now
            elapsed = now - self.last_updates[sys_key]
            if elapsed < sys.periodicity_sec:
                continue
            self.last_updates[sys_key] = now

            try:
                status.load(sys.update(self.db, elapsed))
            except Exception as e:
                logger.error(f'{sys.__class__.__name__}: {e}\n{traceback.format_exc()}')
        self.apply_demography(status)

    @time_func
    def apply_demography(self, status: Demography):
        ids = self.db.update_demography(status)
        for sys in self.systems:
            self.update_demography(sys, status)
        return ids

    @time_func
    def update_demography(self, sys: System, status: Demography):
        if sys._signature is None:
            return

        index = self.db.get_index(sys)
        items = index.items
        for _ in status.death:
            item = items.pop(_, None)
            if item:
                sys.unregister(item)
        for _ in status.birth:
            if isinstance(_, Component):
                _ = [_]
            item = sys.cast(_)
            if item is not None:
                if item.eid not in items:
                    items[item.eid] = item
                    sys.register(item)


# default simulator
sim = ECS()
