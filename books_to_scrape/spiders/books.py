import re
from pathlib import Path
from types import new_class

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response: Response, **kwargs):
        book_detail_links = response.css("h3 > a::attr(href)").getall()

        yield from response.follow_all(book_detail_links, self._parse_book)

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book(self, response: Response, **kwargs) -> float:
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get()[1:]),
            "amount_in_stock": int(
                response.css("tr th:contains('Availability') + td::text")
                .get()
                .split("(")[-1]
                .split(" ")[0]
            ),
            "rating": int(
                rating[response.css("p.star-rating::attr(class)").get().split()[-1]]
            ),
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description": response.css("article > p::text").get(),
            "upc": response.css("tr th:contains('UPC') + td::text").get(),
        }
