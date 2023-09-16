import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        book_page_link = response.css("h3 > a:last-child::attr(href)")
        yield from response.follow_all(
            book_page_link, callback=self.parse_book_detail_page
        )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_book_detail_page(self, response: Response):
        amount_in_stock = (
            response.css("p.instock.availability").get().split("\n ")[-2]
        )
        rating_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(re.findall(r'\d+', amount_in_stock)[0]),
            "rating": rating_dict[
                response.css(".star-rating::attr(class)").get().split()[-1]
            ],
            "category": response.css(
                ".breadcrumb > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css("table > tr:first-child > td::text").get()
        }
