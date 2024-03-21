from typing import Generator

import scrapy
from scrapy.http import Response

RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books_1/index.html"
    ]

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css("li.col-xs-6.col-sm-4.col-md-3.col-lg-3"):
            yield response.follow(
                book.css(
                    "article.product_pod > div.image_container > a::attr(href)"
                ).get(),
                callback=self.parse_detail_page
            )
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_detail_page(response: Response) -> dict:
        return {
            "title": response.css("div.product_main > h1::text").get(),
            "price": float(response.css("p.price_color::text").get()[1:]),
            "amount_in_stock": int(
                response.css(
                    "table.table.table-striped td:contains('In stock')::text"
                ).get().split()[2].replace("(", "")
            ),
            "rating": RATINGS.get(
                response.css("p.star-rating::attr(class)").get().split()[1]
            ),
            "category": response.css(
                "ul.breadcrumb > li > a::text"
            ).getall()[2],
            "description": response.css(
                "article.product_page > p::text"
            ).get(),
            "UPC": response.css(
                "table.table.table-striped td::text"
            ).get()
        }
