from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        url = "https://books.toscrape.com/"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            yield scrapy.Request(
                response.urljoin(book.css("a::attr(href)").get()),
                callback=self.parse_detail,
            )

        if next_page := response.css(".next a::attr(href)").get():
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_detail(response: Response) -> dict[str, str | float | int]:
        return {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(response.css(
                ".availability::text").re_first(r"\d+")
            ),
            "rating": response.css(".star-rating::attr(class)")
            .get()
            .split(" ")[1],
            "category": response.css(
                ".breadcrumb > li:nth-child(3) a::text"
            ).get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css("td::text").get(),
        }
