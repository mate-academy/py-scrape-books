from typing import Iterable

import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"

    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "AUTOTHROTTLE_MAX_DELAY": 60,
    }

    start_urls = [
        (f"https://books.toscrape.com/catalogue/page-{i}"
         f".html") for i in range(1, 51)
    ]

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Iterable[scrapy.Request]:
        books = response.css("article.product_pod")

        for book in books:
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, callback=self.parse_book_details)

    def parse_book_details(
            self,
            response: Response,
            **kwargs
    ) -> Iterable[BooksItem]:
        main = response.css(".product_main")

        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_text = rating_class.split()[-1] if rating_class else "Zero"

        price_raw = main.css(".price_color::text").re_first(r"\d+\.\d+")
        stock_raw = response.css(".availability::text").re_first(r"\d+")

        item = BooksItem()
        item["title"] = main.css("h1::text").get()
        item["price"] = float(price_raw) if price_raw else 0.0
        item["amount_in_stock"] = int(stock_raw) if stock_raw else 0
        item["rating"] = rating_map.get(rating_text, 0)
        item["category"] = response.css(
            ".breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css(
            "#product_description + p::text").get()
        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td[1]/text()").get()

        yield item
