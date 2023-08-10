import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    stars = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".product_pod > h3 > a")
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_book(self, response):
        def get_table() -> list:
            return response.css("td::text").getall()

        yield {
            "title": response.css("div.product_main > h1::text").get(),
            "price": float(response.css("div.product_main > .price_color::text").get().replace("£", "")),
            "amount_in_stock": int(*re.findall(r"\d+", response.css("p.instock").get())),
            "rating": int(self.stars[response.css(".star-rating::attr(class)").get().split()[-1]]),
            "category": get_table()[1],
            "description": response.css("article > p::text").get(),
            "upc": get_table()[0],
        }
