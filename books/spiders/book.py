import scrapy
from scrapy.http import Response
from collections.abc import Generator
from typing import Optional, Union


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com//"]

    def parse(self,
              response: Response,
              **kwargs: Optional[dict]
              ) -> Generator[scrapy.Request, None, None]:
        books_links = (
            response.css(".product_pod > .image_container")
            .css("a::attr(href)")
            .getall()
        )
        yield from response.follow_all(
            books_links, callback=self.parse_single_book
        )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def book_rating(response: Response) -> Union[int, str]:
        star_ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        for string, integer in star_ratings.items():
            if response.css(f".product_main > p.{string}").get() is not None:
                return integer

    def parse_single_book(self, response: Response) -> Generator[dict, None, None]:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": response.css(".instock").get().split()[7][1:],
            "rating": self.book_rating(response),
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + *::text"
            ).get(),
            "upc": response.css(
                ".table.table-striped > tr:first-child > td::text"
            ).get(),
        }
