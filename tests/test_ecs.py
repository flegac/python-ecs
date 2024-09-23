import uuid
from typing import override

from easy_kit.timing import TimingTestCase
from pydantic import Field

from python_ecs.component import Component, Signature
from python_ecs.ecs import ECS
from python_ecs.entity_filter import FilterStrategy
from python_ecs.storage.database import Database
from python_ecs.system import System
from python_ecs.demography import Demography


class Position(Component):
    x: int = 0
    y: int = 0


class Speed(Component):
    x: int = 0
    y: int = 0


class Info(Component):
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))


class Move(Signature):
    pos: Position
    speed: Speed


class MoveSystem(System[Move]):
    _signature = Move

    @override
    def update_single(self, db: Database, item: Move, dt: float):
        item.pos.x += item.speed.x
        item.pos.y += item.speed.y
        if item.pos.x > 3:
            return Demography().with_death(item.eid)
        if item.speed.y == 0:
            return Demography().with_birth([
                [Info()],
                [Info()],
                [Info(), Position(x=0, y=10), Speed(x=0, y=2)],
                [Info(), Position(x=100, y=100)],
            ])


class LogSystem(System):
    _filter_strategy = FilterStrategy.match_all

    @override
    def update_single(self, db: Database, item: list[Component], dt: float):
        eid = None
        for _ in filter(None, items):
            eid = _.eid
            break
        print(f'{eid}: {items}')


class TestEcs(TimingTestCase):

    def test_ecs(self):
        # init systems
        ecs = ECS(systems=[
            LogSystem(),
        ])

        # create some entities
        demography = Demography().with_birth([
            Info(),
            [Info(), Position(x=3)],
            [Info(), Speed(x=2, y=1)],
            [Position(y=2), Speed(y=2)],
            [Info(), Position(x=6, y=6), Speed(x=2, y=1)],
            [Info(), Position(x=2, y=2), Speed(x=0, y=0)],
        ])
        ecs.apply_demography(demography)

        # run simulation
        print('* update')
        ecs.update()
        print('* update')
        ecs.update()

        # update systems
        ecs.systems.insert(0, MoveSystem())

        print('* update (move)')
        ecs.update()

        print('update (move)')
        ecs.update()
