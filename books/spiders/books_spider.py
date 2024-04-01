import scrapy
from scrapy.http import Response

from typing import Any


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        # get books detail info
        yield from response.follow_all(
            css=".product_pod h3 a", callback=self.parse_author
        )

        # next page
        yield from response.follow_all(
            css=".pager .next a", callback=self.parse
        )

    def parse_author(self, response: Response, **kwargs):
        ratings = dict(Zero=0, One=1, Two=2, Three=3, Four=4, Five=5)
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css('p.instock.availability').re(r"\d+")[0]
            ),
            "rating": ratings[
                response.css(".star-rating").attrib["class"].split()[1]
            ],
            "category": response.css(
                ".breadcrumb li"
            )[2].css("a::text").get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(
                ".table-striped th:contains('UPC') + td::text"
            ).get()
        }
