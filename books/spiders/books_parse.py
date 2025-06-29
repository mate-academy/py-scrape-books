import re
from typing import Generator, Any

import scrapy
from scrapy import Request
from scrapy.http import Response
from books.items import BookItem


class BooksParseSpider(scrapy.Spider):
    name = "books_parse"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_single_book(self, response: Response
                          ) -> Generator[Request, Any, None]:
        item = BookItem()

        item["title"] = response.css(
            "h1::text").get()
        item["price"] = response.css(
            ".price_color::text").get()

        category_raw = response.css(
            "ul.breadcrumb li:nth-child(3) a::text").get()
        if category_raw:
            item["category"] = category_raw.strip()
        else:
            item["category"] = None

        item["description"] = response.css(
            "#product_description + p::text").get()

        # UPC & amount_in_stock
        for row in response.css("table.table-striped tr"):
            header = row.css("th::text").get()
            value = row.css("td::text").get()
            if header == "UPC":
                item["upc"] = value
            elif header == "Availability":
                match = re.search(
                    r"\((\d+) available\)",
                    value)
                if match:
                    item[
                        "amount_in_stock"
                    ] = int(match.group(1))

        # Rating
        rating_text = response.css(
            "p.star-rating::attr(class)").get().replace(
            "star-rating ", "")
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        item["rating"] = rating_map.get(rating_text, 0)

        yield item

    def parse(self, response: Response, **kwargs
              ) -> Generator[Request, Any, None]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
