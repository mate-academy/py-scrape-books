import re
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            detailed_url = urljoin(response.url, book_url)
            yield scrapy.Request(
                url=detailed_url, callback=self.parse_books
            )

        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    @staticmethod
    def parse_books(response):
        availability_text = response.css(
            "p.instock.availability::text"
        ).getall()
        amount_in_stock = 0

        for text in availability_text:
            match = re.search(r"\d+", text)
            if match:
                amount_in_stock = int(match.group())
                break

        yield {
            "title": response.css("h1::text").get(),
            "price": (
                response.css("p.price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": amount_in_stock,
            "rating": (
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ),
            "category": (
                response.css(
                    "ul.breadcrumb > li:nth-last-child(2) > a::text"
                ).get()
            ),
            "description": response.css(".product_page > p::text").get(),
            "UPC": response.css('th:contains("UPC") + td::text').get(),
        }
