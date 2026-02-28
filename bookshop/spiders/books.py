import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def convert_rating(self, rating_text):
        return self.RATING_MAP.get(rating_text)

    def parse(self, response: Response):
        for book in response.css("article.product_pod"):
            rating_class = book.css("p.star-rating::attr(class)").get()
            rating_text = rating_class.split()[-1] if rating_class else None

            detail_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                detail_url,
                callback=self.parse_book,
                meta={
                    "title": book.css("h3 a::attr(title)").get(),
                    "price": float(book.css(".price_color::text").get().replace("£", "")),
                    "rating": int(self.convert_rating(rating_text)),
                },
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        yield {
            "title": response.meta["title"],
            "price": response.meta["price"],
            "rating": response.meta["rating"],
            "amount_in_stock": self._parse_amount_in_stock(response),
            "category": self._parse_category(response),
            "description": self._parse_description(response),
            "upc": self._parse_upc(response),
        }

    def _parse_amount_in_stock(self, response: Response):
        try:
            text = response.xpath("normalize-space(//p[contains(@class,'instock')])").get()
            if text:
                match = re.search(r"\d+", text)
                if match:
                    return int(match.group())
        except Exception as e:
            self.logger.warning(f"Cannot parse stock: {e}")
        return 0

    def _parse_category(self, response: Response):
        return response.css(".breadcrumb li:nth-child(3) a::text").get()

    def _parse_description(self, response: Response):
        return response.css("#product_description + p::text").get()

    def _parse_upc(self, response: Response):
        return response.css("th:contains('UPC') + td::text").get()


# import scrapy
# from scrapy.http import Response
# from selenium import webdriver
# from twisted.internet.defer import Deferred
#
#
# class BooksSpider(scrapy.Spider):
#     name = "books"
#     allowed_domains = ["books.toscrape.com"]
#     start_urls = ["https://books.toscrape.com/"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.driver = webdriver.Chrome()
#
#     def close(self, reason: str) -> Deferred[None] | None:
#         self.driver.close()
#         return self.close(reason)
#
#     RATING_MAP = {
#         "One": 1,
#         "Two": 2,
#         "Three": 3,
#         "Four": 4,
#         "Five": 5,
#     }
#
#     def convert_rating(self, rating_text):
#         return self.RATING_MAP.get(rating_text)
#
#
#     def parse(self, response: Response, **kwargs):
#         for book in response.css("article.product_pod"):
#             rating_text = book.css("p.star-rating::attr(class)").get().split()[-1]
#             yield {
#                 "title": book.css("h3 a::attr(title)").get(),
#                 "price": float(book.css(".price_color::text").get().replace("£", "")),
#                 "rating": int(self.convert_rating(rating_text)),
#                 "amount_in_stock": self._parse_amount_in_stock(response, book),
#                 "category": self._parse_category(response, book),
#                 "description": self._parse_description(response, book),
#                 "upc": self._parse_upc(response, book),
#             }
#         next_page = response.css("ul.pager li.next a::attr(href)").get()
#         if next_page is not None:
#             yield response.follow(next_page, callback=self.parse)
#
#
#     def _parse_amount_in_stock(self, response: Response, book):
#         pass
#
#
#     def _parse_category(self, response: Response, book):
#         pass
#
#
#     def _parse_description(self, response: Response, book):
#         pass
#
#
#     def _parse_upc(self, response: Response, book):
#         pass





