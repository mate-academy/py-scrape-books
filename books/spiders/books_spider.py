import re

import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(book, callback=self.parse_single_book)

        next_page = response.css(".pager > li.next").css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response) -> dict:
        title = response.css("h1::text").get()
        price = float(
            response.css(".price_color::text").get().replace("£", "")
        )
        stock_text = response.css(".table-striped td::text").getall()[-2]
        amount_in_stock = int(re.search(r'\d+', stock_text).group(0))
        rating_text = response.css(
            ".star-rating::attr(class)"
        ).get().split(" ")[-1]
        rating = self.RATING_MAP.get(rating_text)
        category = response.css(
            ".breadcrumb li:nth-last-child(2) a::text"
        ).get()
        description = response.css("#product_description ~ p::text").get()
        upc = response.css(".table-striped td::text").getall()[0]

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
