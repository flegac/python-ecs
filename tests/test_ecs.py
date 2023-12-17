import uuid

from pydantic import Field

from easy_lib.timing import TimingTestCase, time_func
from python_ecs.ecs import Component, System, ECS, UpdateStatus
from python_ecs.log_system import LogSystem


class Position(Component):
    x: int = 0
    y: int = 0


class Speed(Component):
    x: int = 0
    y: int = 0


class Info(Component):
    name: str = Field(default_factory=lambda: str(uuid.uuid4()))


class MoveSystem(System):
    @staticmethod
    def create():
        return MoveSystem(signature=[Position, Speed])

    @time_func
    def update(self, pos: Position, speed: Speed):
        pos.x += speed.x
        pos.y += speed.y
        if pos.x > 3:
            return UpdateStatus.dead(pos.eid)


class TestEcs(TimingTestCase):

    def test_ecs(self):
        # init systems
        sim = ECS(systems=[
            LogSystem(signature=[Position, Speed]),
        ])

        # create some entities
        sim.new_entities([
            [Info(), Position(x=3)],
            [Position(y=2), Speed(y=2)],
            [Info(), Position(x=6, y=6), Speed(x=2, y=1)],
            [Info(), Speed(x=2, y=1)],
            [Info()]
        ])

        # run simulation
        print('* update')
        sim.update()
        print('* update')
        sim.update()

        # update systems
        sim.systems.insert(0, MoveSystem.create())

        print('* update (move)')
        sim.update()

        print('update (move)')
        sim.update()
