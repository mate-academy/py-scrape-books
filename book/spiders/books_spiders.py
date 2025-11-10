import re
from typing import AsyncGenerator, Any, Generator

from scrapy import Request
from scrapy.http import Response
import scrapy

from book.utils import scrap_pagination_urls


class BookSpider(scrapy.Spider):
    name = "books"
    rating_dict = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    async def start(self) -> AsyncGenerator[Request, None]:
        urls = scrap_pagination_urls("https://books.toscrape.com")
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Generator[Request, None, None]:
        urls = response.css(
            ".product_pod h3 a::attr(href)"
        ).getall()
        yield from response.follow_all(urls, self.parse_single_book)

    def parse_single_book(
            self,
            response: Response
    ) -> Generator[
        dict[str, float | int | Any], None, None
    ]:
        main_block = response.css(".product_main")
        match = re.search(
            r"\((\d+)\s+available\)",
            main_block.css(".instock").get()
        )
        category_location = response.css(".breadcrumb li")[2]
        upc_location = response.css(".table tr")[0]
        yield {
            "title": main_block.css("h1::text").get(),

            "price": float(main_block.css(
                ".price_color::text"
            ).get().replace("£", "")),

            "amount_in_stock": int(match.group(1)) if match else 0,

            "rating": self.rating_dict[main_block.css(
                ".star-rating::attr(class)"
            ).get().replace("star-rating ", "")],

            "category": category_location.css("a::text").get(),

            "description": response.css("#product_description + p::text").get(),

            "upc": upc_location.css("td::text").get()
        }
