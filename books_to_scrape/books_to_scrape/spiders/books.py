from typing import Generator

import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def get_single_book(response: Response) -> Generator[dict, None, None]:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get()[1:],
            "amount_in_stock": response.css(
                ".instock.availability::text"
            ).re_first(r"\d+"),
            "rating": w2n.word_to_num(
                response.css(".star-rating::attr(class)").get().split(" ")[-1]
            ),
            "category": response.css("a[href*='category']::text").getall()[-1],
            "description": response.css("#product_description+p::text").get(),
            "upc": response.css("td::text").get(),
        }

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[scrapy.Request, None, None]:
        for book in response.css("h3 a"):
            yield response.follow(book, callback=self.get_single_book)

        for next_url in response.css(".next a"):
            yield response.follow(next_url, callback=self.parse)
