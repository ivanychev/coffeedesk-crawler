import dataclasses
import re
from datetime import date, datetime

from bs4.element import Tag
from typing import Self

DATE_RE = re.compile(r"\d{2}.\d{2}.\d{4}")


@dataclasses.dataclass
class Coffee:
    name: str
    link: str
    image_url: str | None
    roasting_date: date | None

    @classmethod
    def parse_from_soup(cls, node: Tag) -> Self:
        a_tag = node.select("a.product-name")[0]
        link = a_tag.attrs["href"]
        name = a_tag.attrs["title"]
        image_url = None
        if image_node := node.select("img.product-image"):
            image_url = image_node[0].attrs["src"]
        roasting_date = None
        if roasting_data := node.select("p.product-box__roasting-data"):
            raw_date = DATE_RE.findall(roasting_data[0].text)[0]
            roasting_date = datetime.strptime(raw_date, "%d.%m.%Y").date()
        return cls(
            name=name, link=link, roasting_date=roasting_date, image_url=image_url
        )

    def asdict(self) -> dict:
        d = dataclasses.asdict(self)
        d["roasting_date"] = (
            None if not d["roasting_date"] else d["roasting_date"].isoformat()
        )
        return d
