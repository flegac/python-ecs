import traceback

import time
from loguru import logger

from easy_kit.timing import time_func, timing
from python_ecs.component import Component
from python_ecs.component_set import ComponentSet
from python_ecs.storage.database import Database
from python_ecs.storage.demography import Demography
from python_ecs.system import System, SystemBag
from python_ecs.types import EntityId


class ECS:
    def __init__(self, systems: list[System] = None):
        self.db = Database()
        self.systems = systems or []
        self.last_updates = {}

    def create_all(self, items: list[ComponentSet]):
        self.db.create_all(items)

    @time_func
    def update(self):
        self.apply_demography()

        now = time.time()
        systems = []
        for _ in self.systems:
            if isinstance(_, SystemBag):
                systems.extend(_.steps)
            else:
                systems.append(_)

        for sys in systems:
            sys_key = sys.__class__
            if sys_key not in self.last_updates:
                self.last_updates[sys_key] = now
            elapsed = now - self.last_updates[sys_key]
            if elapsed < sys.periodicity_sec:
                continue
            self.last_updates[sys_key] = now

            try:
                with timing(f'ECS.{sys.__class__.__name__}.update'):
                    sys.update(self.db, elapsed)
            except Exception as e:
                logger.error(f'{sys.__class__.__name__}: {e}\n{traceback.format_exc()}')
        self.apply_demography()

    @time_func
    def apply_demography(self):
        status = Demography().load(self.db.dirty)
        self.db.dirty.clear()

        systems = [_ for _ in self.systems if _._signature is not None]
        for sys in systems:
            for _ in status.death:
                self._handle_death(sys, _)
        for sys in systems:
            for _ in status.birth:
                self._handle_birth(sys, _)

        self.db.update_demography(status)

    def _handle_birth(self, sys: System, items: Component | list[Component]):
        if isinstance(items, Component):
            items = [items]
        signature = sys._signature
        item = signature.cast(items)
        if item is not None:
            self.db.get_table(signature).create(item)
            sys.register(item)

    def _handle_death(self, sys: System, eid: EntityId):
        index = self.db.get_table(sys._signature)
        item = index.read(eid)
        if item:
            sys.unregister(item)
        index.destroy(eid)


# default simulator
sim = ECS()
