import httpx
from bs4 import BeautifulSoup
from furl import furl
from loguru import logger

from coffeedesk.coffee import Coffee
from coffeedesk.filters.request import RequestFilter

ENDPOINT = (
    "https://www.coffeedesk.pl/widgets/cms/navigation/ac9d993721af3405c2059beb5e91569d"
)


def fetch_coffee(
    request_filter: RequestFilter, max_pages: int | None = None
) -> list[Coffee]:
    max_pages = max_pages if max_pages is not None else float("+inf")
    has_output = True
    page = 0
    raw_product_nodes = []
    while has_output:
        page += 1
        if page > max_pages:
            break
        u = furl(ENDPOINT)
        u.args["order"] = "dostepnosc"
        u.args["properties"] = "|".join(request_filter.ids)
        u.args["p"] = page
        logger.info("Fetching page {} ...", page)

        resp = httpx.get(str(u))
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        page_raw_product_nodes = soup.select(".product-box")
        logger.info("Fetched {} pages", len(page_raw_product_nodes))
        has_output = bool(len(page_raw_product_nodes))
        raw_product_nodes.extend(page_raw_product_nodes)
    return [Coffee.parse_from_soup(node) for node in raw_product_nodes]
