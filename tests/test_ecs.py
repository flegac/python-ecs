import uuid
from typing import Type

from pydantic import Field

from easy_lib.timing import TimingTestCase, time_func
from python_ecs.ecs import Component, System, ECS, UpdateStatus, Signature
from python_ecs.log_system import LogSystem


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


class MoveSystem(System):
    signature: Type[Signature] = Move

    @time_func
    def update(self, item: Move):
        item.pos.x += item.speed.x
        item.pos.y += item.speed.y
        if item.pos.x > 3:
            return UpdateStatus.dead(item.eid)
        if item.speed.y == 0:
            return UpdateStatus.create([
                [Info()],
                [Info()],
                [Info(), Position(x=0, y=10), Speed(x=0, y=2)],
                [Info(), Position(x=100, y=100)],
            ])


class TestEcs(TimingTestCase):

    def test_ecs(self):
        # init systems
        sim = ECS(systems=[
            LogSystem(),
        ])

        # create some entities
        sim.new_entities([
            [Info()],
            [Info(), Position(x=3)],
            [Info(), Speed(x=2, y=1)],
            [Position(y=2), Speed(y=2)],
            [Info(), Position(x=6, y=6), Speed(x=2, y=1)],
            [Info(), Position(x=2, y=2), Speed(x=0, y=0)],
        ])

        # run simulation
        print('* update')
        sim.update()
        print('* update')
        sim.update()

        # update systems
        sim.systems.insert(0, MoveSystem())

        print('* update (move)')
        sim.update()

        print('update (move)')
        sim.update()
