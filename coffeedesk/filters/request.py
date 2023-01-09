import dataclasses

from typing import Self

from coffeedesk.filters.parser import CoffeeDeskFilters


@dataclasses.dataclass(frozen=True)
class RequestFilter:
    ids: frozenset[str]


class RequestFilterBuilder:
    def __init__(self, filters: CoffeeDeskFilters):
        self.filters = filters
        self.selected_ids = set()

    def with_pure_arabica(self) -> Self:
        self.selected_ids.add(self.filters.arabica["100% Arabica"])
        return self

    def with_whole_beans(self) -> Self:
        self.selected_ids.add(self.filters.coffee_type["Ziarnista"])
        return self

    def build(self) -> RequestFilter:
        return RequestFilter(frozenset(self.selected_ids))
