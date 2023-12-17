from python_ecs.ecs import System, CFilter


class LogSystem(System):
    component_filter: CFilter = CFilter.match_all

    def update(self, *args):
        eid = None
        for _ in filter(None, args):
            eid = _.eid
            break
        print(f'{eid}: {args}')
