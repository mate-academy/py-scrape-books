from typing import Generator, Any

import scrapy
from scrapy import Request

from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[Any]:
        for card in response.css(".product_pod"):
            detailed_url = response.urljoin(card.css("a::attr(href)").get())
            yield scrapy.Request(url=detailed_url, callback=self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_single_book(response: Response) -> Generator[dict]:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                response.css(".instock.availability::text").re_first(r"\d+")
            ),
            "rating": response.css("p.star-rating::attr(class)").get().split()[1],
            "category": response.css(".breadcrumb > li:nth-child(3) a::text").get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css(".table tr:nth-child(1) td::text").get(),
        }
