from typing import Dict
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Dict:
        for book in response.css(".product_pod"):
            yield scrapy.Request(
                url=urljoin(response.url, book.css("h3 > a::attr(href)").get()),
                callback=self.get_single_book,
            )

        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_single_book(response: Response) -> Dict:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                response.css(".instock.availability::text").re_first(
                    r"\((\d+) available\)"
                )
            ),
            "rating": RATINGS.get(
                response.css(".star-rating::attr(class)").get().split()[1], 0
            ),
            "category": response.css(".breadcrumb > li > a::text").getall()[-1],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table.table-striped > tr")[0].css("td::text").get(),
        }
