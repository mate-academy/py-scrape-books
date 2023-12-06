from __future__ import annotations

from word2number import w2n

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs):
        list_of_detailed_links = response.css("h3 a::attr(href)").getall()
        for link in list_of_detailed_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> dict[str, str] | None:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                response.css(".instock.availability").re_first(r"\d+")
            ),
            "rating": w2n.word_to_num(
                response.css(".star-rating::attr(class)").get().split()[1]
            ),
            "category": response.css(".breadcrumb > li:nth-child(3) > a::text").get(),
            "description": response.css("#content_inner > article > p::text").get(),
            "upc": response.css(
                ".table.table-striped > tr:nth-child(1) > td::text"
            ).get(),
        }
