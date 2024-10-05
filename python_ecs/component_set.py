from python_ecs.component import Component
from python_ecs.signature import Signature

ComponentSet = Component | list[Component] | Signature | None


def flatten_components(item: ComponentSet):
    if isinstance(item, Component):
        return [item]
    if isinstance(item, Signature):
        return item.to_components()
    return item
