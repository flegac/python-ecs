from enum import Enum, auto
from typing import Type, Self, Iterable

from pydantic import Field

from easy_lib.my_model import MyModel
from easy_lib.timing import time_func


class GenId:
    def __init__(self):
        self._next_id = 0

    def new_id(self):
        self._next_id += 1
        return self._next_id


type ComponentId = int
type EntityId = int

CID_GEN = GenId()
EID_GEN = GenId()


class Component(MyModel):
    cid: ComponentId = Field(default_factory=CID_GEN.new_id)
    eid: EntityId = -1
    active: bool = True

    @property
    def type_id(self):
        return self.__class__

    def __str__(self):
        params = ', '.join(f"{k}: {v}" for k, v in self.__dict__.items() if k not in {'cid', 'eid'})
        return f'{self.type_id.__name__}({params})'

    def __repr__(self):
        return str(self)


class UpdateStatus(MyModel):
    dead_entities: set[EntityId] = Field(default_factory=set)
    new_entities: list[list[Component]] = Field(default_factory=list)

    @staticmethod
    def dead(eid: EntityId):
        return UpdateStatus(dead_entities={eid})

    @staticmethod
    def new(items: list[list[Component]]):
        return UpdateStatus(new_entities=items)

    @time_func
    def load(self, other: Self):
        if other is None:
            return
        self.dead_entities.update(other.dead_entities)
        self.new_entities.extend(other.new_entities)


class CFilter(str, Enum):
    requires_all = auto()
    requires_any = auto()
    match_all = auto()


class System(MyModel):
    signature: list[Type[Component]]
    component_filter: CFilter = CFilter.requires_all

    @time_func
    def update_all(self, items: list[list[Type[Component | None]]]):
        status = UpdateStatus()
        for _ in items:
            status.load(self.update(*_))
        return status

    def update(self, *args, **kwargs) -> UpdateStatus | None:
        """
        :param args: components in same order as the List[Type[Component]]
        :param kwargs: named parameter list : 'Component.type_id = component' (ex: MyComponent = component_instance)
        :return:
        """
        raise NotImplementedError


class Components(MyModel):
    ctype: Type[Component]
    active: dict[EntityId, Component] = Field(default_factory=dict)
    inactive: dict[EntityId, Component] = Field(default_factory=dict)

    def remove(self, eid: EntityId):
        self.active.pop(eid, None)
        self.inactive.pop(eid, None)

    def remove_all(self, eids: Iterable[EntityId]):
        for _ in eids:
            self.remove(_)

    def add(self, eid: int, component: Component):
        component.eid = eid
        if component.active:
            self.active[eid] = component
        else:
            self.inactive[eid] = component


class ECS(MyModel):
    systems: list[System] = Field(default_factory=list)
    components: dict[Type[Component], Components] = Field(default_factory=dict)

    @property
    @time_func
    def entities(self) -> set[EntityId]:
        return set().union(*[set(_.active.keys()) for _ in self.components.values()])

    @time_func
    def union_entities(self, signature: list[Type[Component]]):
        res = set()
        for _ in signature:
            res.update(self.components[_].active.keys())
        return res

    @time_func
    def common_entities(self, signature: list[Type[Component]]):
        if not signature:
            return set()
        first = signature[0]
        res = set(self.components[first].active.keys())
        for _ in signature[1:]:
            res.intersection_update(self.components[first].active.keys())
            if not res:
                return res
        return res

    @time_func
    def new_entities(self, entities: list[list[Component]]):
        for components in entities:
            eid = EID_GEN.new_id()
            for c in components:
                ctype = c.type_id
                if ctype not in self.components:
                    self.components[ctype] = Components(ctype=ctype)
                self.components[ctype].add(eid, c)

    @time_func
    def destroy(self, ids: Iterable[EntityId]):
        for c in self.components.values():
            c.remove_all(ids)

    @time_func
    def update(self):
        status = UpdateStatus()
        for sys in self.systems:
            items = self.compute_components(sys)
            status.load(sys.update_all(items))
        self.destroy(status.dead_entities)
        self.new_entities(status.new_entities)

    @time_func
    def compute_components(self, sys: System):
        match sys.component_filter:
            case CFilter.match_all:
                signature = list(self.components.keys())
                entities = self.entities
            case CFilter.requires_all:
                signature = sys.signature
                entities = self.common_entities(signature)
            case CFilter.requires_any:
                signature = sys.signature
                entities = self.union_entities(signature)
            case _:
                raise NotImplementedError
        return [
            [self.components[_].active.get(eid) for _ in signature]
            for eid in entities
        ]


# default simulator
sim = ECS()
