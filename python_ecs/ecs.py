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


class ECS(MyModel):
    systems: list[System] = Field(default_factory=list)
    components: dict[Type[Component], dict[EntityId, Component]] = Field(default_factory=dict)

    @time_func
    def new_entities(self, entities: list[list[Component]]):
        for e in entities:
            eid = EID_GEN.new_id()
            for c in e:
                self._add_component(eid, c)

    @time_func
    def destroy(self, ids: Iterable[EntityId]):
        for c in self.components.values():
            for eid in ids:
                c.pop(eid, None)

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
        signature = sys.signature
        components = {
            _: self.components.get(_, {})
            for _ in signature
        }

        match sys.component_filter:
            case CFilter.match_all:
                signature = list(self.components.keys())
                entities = set.union(*[set(_.keys()) for _ in self.components.values()])
            case CFilter.requires_all:
                entities = set.intersection(*[set(_.keys()) for _ in components.values()])
            case CFilter.requires_any:
                entities = set.union(*[set(_.keys()) for _ in components.values()])

        return [
            [self.components[ctype].get(eid) for ctype in signature]
            for eid in entities
        ]

    def _add_component(self, eid: int, component: Component):
        component.eid = eid
        comp_type = component.type_id
        if comp_type not in self.components:
            self.components[comp_type] = {}
        self.components[comp_type][eid] = component


# default simulator
sim = ECS()
