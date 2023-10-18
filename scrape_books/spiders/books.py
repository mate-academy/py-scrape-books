import re
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]
    base = "https://books.toscrape.com/catalogue/"
    urls = []

    @staticmethod
    def get_rating(text: str) -> int:
        number_str = text.split()[-1]
        number_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        return number_dict.get(number_str)

    def parse(self, response: Response, **kwargs) -> dict:
        for product in response.css(".product_pod"):
            yield self.urls.append(
                urljoin(self.base, product.css("a::attr(href)").get())
            )

        next_page = response.css(".next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, self.parse)

        for url in self.urls:
            yield scrapy.Request(url, callback=self.parse_book)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": re.sub(
                r"[^0-9]", "", (response.css("td::text").getall()[-2])
            ),
            "rating": self.get_rating(response.css(
                "p.star-rating::attr(class)"
            ).get()),
            "category": response.css("li:nth-last-of-type(2) > a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css("td::text").get(),
        }
