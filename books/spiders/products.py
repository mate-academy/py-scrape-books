from pathlib import Path

import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        """Parse list of books and proceed to every book`s page."""
        for product in response.css("article.product_pod"):
            book_url = response.urljoin(product.css("h3 a::attr(href)").get())

            yield response.follow(book_url, callback=self.parse_book)

    def parse_book(self, response: Response):
        """Parse the exact book`s page in order to get all details"""

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("tr:contains('Availability') td::text").re_first(r"\d+"),  # Шукаємо число
            "rating": response.css("p.star-rating::attr(class)").re_first(r"star-rating (\w+)"),
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description": response.css("div#product_description ~ p::text").get(),
            "upc": response.css("table.table-striped tr:nth-child(1) td::text").get()
        }
