from python_ecs.ecs import sim, Component, System


class XComponent(Component):
    def __init__(self, x: int) -> None:
        super().__init__()
        self.position = x

    def __repr__(self):
        return '{}: {}, x={}'.format(self.type_id.__name__, self.eid, self.position)


class YComponent(Component):
    def __init__(self, y: int) -> None:
        super().__init__()
        self.position = y

    def __repr__(self):
        return '{}: {}, y={}'.format(self.type_id.__name__, self.eid, self.position)


class MoveSystem(System):
    def __init__(self):
        super().__init__([XComponent, YComponent])

    def update(self, x: XComponent, y: YComponent) -> None:
        x.position += 1
        y.position += 2


class LogSystem(System):
    def __init__(self, ctype: Component.Type):
        super().__init__([ctype])

    def update(self, c: Component):
        print(c)


def test_ecs():
    # init systems
    sim.reset_systems([
        MoveSystem(),
        LogSystem(XComponent),
        LogSystem(YComponent)
    ])

    # create some entities
    sim.create(XComponent(x=3))

    sim.create() \
        .attach(XComponent(x=1)) \
        .attach(YComponent(y=2))

    sim.create(
        XComponent(x=6),
        YComponent(y=6)
    )

    # run simulation
    print('update')
    sim.update()

    print('update')
    sim.update()
