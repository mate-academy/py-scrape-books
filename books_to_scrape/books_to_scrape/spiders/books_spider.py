import re
from typing import Any, Generator

import scrapy
from scrapy import Request
from scrapy.http import Response

from books_to_scrape.items import Book


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/category/books_1/page-1.html"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0,
        "CONCURRENT_REQUESTS": 20,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 20,
        "COOKIES_ENABLED": False,
        "LOG_LEVEL": "INFO",
    }

    def parse_detail(self, response: Response, **kwargs) -> Generator[Book, Any, None]:
        convert_word = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        price_text = response.css(".price_color::text").get()
        in_stock_string = response.css(".instock").re_first(r"\((\d+) available\)")
        rating_string = response.css(".star-rating::attr(class)").get()
        rating_val = rating_string.split(" ")[-1] if rating_string else ""

        price_match = re.search(r"[\d.]+", price_text)
        price = float(price_match.group(0)) if price_match else 0.0
        amount_in_stock = int(in_stock_string) if in_stock_string else 0
        rating = int(convert_word.get(rating_val, 0))

        title = response.css("div.product_main h1::text").get()
        category = response.css(".breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get()
        upc = response.css("table tr:nth-child(1) td::text").get()

        yield Book(
            title=title.strip() if title else None,
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category.strip() if category else None,
            description=description.strip() if description else None,
            upc=upc.strip() if upc else None,
        )

    def parse(self, response: Response, **kwargs) -> Generator[Request, Any, None]:
        for book_pod in response.css(".product_pod"):
            detail_url = book_pod.css("h3 a::attr(href)").get()
            yield response.follow(detail_url, callback=self.parse_detail)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
