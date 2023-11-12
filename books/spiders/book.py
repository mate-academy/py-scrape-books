from typing import Generator

import scrapy
from scrapy.http import Response
from scrapy.spiders.sitemap import re


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[dict, None, None]:
        book_links = response.css(".product_pod > h3 > a::attr(href)")
        yield from response.follow_all(book_links, callback=self.parse_book)

        next_links = response.css(".pager > .next > a::attr(href)")
        yield from response.follow_all(next_links, callback=self.parse)

    def parse_book(
        self, response: Response, **kwargs
    ) -> Generator[dict, None, None]:
        rating_mappings = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
        }

        title = response.css(".product_main > h1::text").get()
        price = re.sub(r"[^\d.]", "", response.css(".price_color::text").get())
        amount_in_stock = re.sub(
            r"[^\d]",
            "",
            response.css(".product_main > .availability::text").getall()[-1],
        )
        rating_word = (
            response.css(".product_main > .star-rating::attr(class)")
            .get()
            .split()[-1]
        )
        category = response.xpath(
            "//*[@class='breadcrumb']/li[a][last()]/a/text()"
        ).get()
        description = response.css("#product_description + p::text").get()
        upc = response.css("table tr:first-child > td::text").get()
        yield {
            "title": title,
            "price": float(price),
            "amount_in_stock": int(amount_in_stock),
            "rating": rating_mappings[rating_word.lower()],
            "category": category,
            "description": description,
            "upc": upc,
        }
