import re

import scrapy
from scrapy.http import Response

from ..items import BookItem


class BooksSpider(scrapy.Spider):

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response, **kwargs):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book_detail)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response):
        book = BookItem()

        book["title"] = self._extract_title(response)
        book["price"] = self._extract_price(response)
        book["amount_in_stock"] = self._extract_stock(response)
        book["rating"] = self._extract_rating(response)
        book["category"] = self._extract_category(response)
        book["description"] = self._extract_description(response)
        book["upc"] = self._extract_upc(response)

        yield book

    def _extract_title(self, response):
        return response.css("div.product_main h1::text").get()

    def _extract_price(self, response):
        price_text = response.css("p.price_color::text").get()
        if price_text:
            price_clean = price_text.replace("£", "").strip()
            try:
                return float(price_clean)
            except ValueError:
                return None
        return None

    def _extract_stock(self, response):
        stock_texts = response.css(
            "div.product_main p.instock.availability::text"
        ).getall()
        stock_info = " ".join(text.strip() for text in stock_texts if text.strip())

        if stock_info:
            match = re.search(r"\((\d+)\s+available\)", stock_info)
            if match:
                return int(match.group(1))
        return None

    def _extract_rating(self, response):
        rating_class = response.css("p.star-rating::attr(class)").get()
        if rating_class:
            rating_word = rating_class.replace("star-rating", "").strip()
            return self.RATING_MAP.get(rating_word)
        return None

    def _extract_category(self, response):
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        return category.strip() if category else None

    def _extract_description(self, response):
        description = response.css("#product_description + p::text").get()
        if not description:
            description = response.css("article.product_page > p::text").get()
        return description.strip() if description else None

    def _extract_upc(self, response):
        upc = response.css("table.table tr:nth-child(1) td::text").get()
        return upc.strip() if upc else None
