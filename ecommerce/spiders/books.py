from collections.abc import Iterator

import scrapy
from scrapy.http import Response

from ecommerce.items import EcommerceItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self,
        response: Response,
        **kwargs,
    ) -> Iterator[scrapy.Request]:
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                book_url,
                callback=self._parse_book,
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book(self, response: Response) -> Iterator[EcommerceItem]:
        amount_in_stock = int(
            response.css("p.instock.availability::text").re_first(r"\d+")
        )

        rating_classes = response.css("p.star-rating::attr(class)").get()
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        rating = rating_map[rating_classes.split()[1]]

        yield EcommerceItem(
            title=response.css(".product_main h1::text").get(),
            price=float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=(
                response.css(".breadcrumb > li")[-2]
                .css("a::text")
                .get()
            ),
            description=response.css(
                "#product_description + p::text"
            ).get(),
            upc=response.css(
                "table.table-striped tr:first-child td::text"
            ).get(),
        )
