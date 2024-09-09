from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[dict, None, None]:

        book_links = response.css(".product_pod a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book(response: Response) -> dict:
        return {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get()[1:]),
            "amount_in_stock": (
                response
                .css("p.instock.availability::text")
                .re_first(r"\d+")
            ),
            "rating": (
                response
                .css("p.star-rating::attr(class)")
                .re_first(r"star-rating (\w+)")
            ),
            "category": (
                response
                .css("ul.breadcrumb > li > a::text")
                .getall()[-1]
            ),
            "description": response.css("article > p::text").get(),
            "upc": (
                response
                .css("table.table.table-striped > tr:nth-child(1) > td::text")
                .get()
            ),
        }
