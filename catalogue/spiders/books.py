from typing import Generator

import scrapy
from scrapy.http import Response

from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[
        scrapy.Request, None, None
    ]:
        for book in response.css(".product_pod"):
            yield scrapy.Request(
                url=response.urljoin(book.css("h3 a::attr(href)").get()),
                callback=self._parse_detail_book
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def _parse_detail_book(response: Response) -> Generator[dict, None, None]:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(
                ".price_color::text"
            ).get().replace("£", ""),
            "amount_in_stock": response.css(
                ".instock.availability::text"
            ).re_first(r"\d+"),
            "rating": w2n.word_to_num(
                response.css(".star-rating::attr(class)").get().split()[-1]
            ),
            "category": response.css(
                "li:nth-last-of-type(2) > a::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css("td::text").get(),
        }
