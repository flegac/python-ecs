from python_ecs.ecs import System, CFilter, Component


class LogSystem(System):
    cfilter: CFilter = CFilter.match_all

    def update(self, items: list[Component]):
        eid = None
        for _ in filter(None, items):
            eid = _.eid
            break
        print(f'{eid}: {items}')
