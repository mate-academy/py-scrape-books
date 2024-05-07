import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book(book: Response):
        yield {"title": book.css(".product_main > h1::text").get(),
               "price": book.css(".price_color::text").get().replace("£", ""),
               "amount_in_stock": "".join(re.findall("[0,9]+", book.css("tr:nth-child(6) td::text").get())),
               "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
               "category": book.css("li:nth-child(3) a::text").get(),
               "description": book.css("article > p::text").get(),
               "upc": book.css("tr:nth-child(1) td::text").get()
               }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".col-lg-3").css("a::attr(href)"):
            yield scrapy.Request(response.urljoin(book.get()), callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
