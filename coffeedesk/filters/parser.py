import dataclasses
from operator import itemgetter

import httpx
from cytoolz import curried, pipe
from typing import Self

ENDPOINT = "https://www.coffeedesk.pl/widgets/cms/navigation/ac9d993721af3405c2059beb5e91569d/filter"

ORIGIN = "Pochodzenie"
ARABICA = "Arabica / Robusta"
PACKAGING = "Opakowanie"
COFFEE_TYPE = "Rodzaj kawy"
ROASTING = "Stopień palenia ziaren"
METHOD = "Przeznaczenie"


def _extract_filters(raw_filters: dict, attribute_name: str) -> dict[str, str]:
    return pipe(
        raw_filters["properties"]["entities"],
        curried.filter(lambda r: r["name"] == attribute_name),
        list,
        itemgetter(0),
        itemgetter("options"),
        curried.map(lambda r: (r["name"], r["groupId"])),
        dict,
    )


@dataclasses.dataclass(frozen=True)
class CoffeeDeskFilters:
    origin: dict[str, str]
    arabica: dict[str, str]
    packaging: dict[str, str]
    coffee_type: dict[str, str]
    roasting: dict[str, str]
    method: dict[str, str]

    @classmethod
    def download_and_parse(cls) -> Self:
        resp = httpx.get(ENDPOINT)
        filters = resp.json()

        return cls(
            origin=_extract_filters(filters, ORIGIN),
            arabica=_extract_filters(filters, ARABICA),
            packaging=_extract_filters(filters, PACKAGING),
            coffee_type=_extract_filters(filters, COFFEE_TYPE),
            roasting=_extract_filters(filters, ROASTING),
            method=_extract_filters(filters, METHOD),
        )
