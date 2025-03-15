from typing import Generator

import scrapy
from scrapy import Selector
from scrapy.http import Response

from books.items import BooksItem

# ran to write the file with books data: scrapy crawl book -O books.jl


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book_card in response.css("article.product_pod"):
            book_details_url = response.urljoin(
                book_card.css("h3 > a::attr(href)").get()
            )

            yield scrapy.Request(
                url=book_details_url, callback=self._parse_book_details
            )

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def _parse_book_details(
        self, response: Response
    ) -> Generator[BooksItem, None, None]:
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        book_details = response.css(".product_page")
        breadcrumb = response.css(".breadcrumb")

        item = BooksItem()

        item["title"] = book_details.css("h1::text").get()

        item["price"] = book_details.css(".price_color::text").get()

        item["amount_in_stock"] = (
            book_details.css("tr:contains('Availability') td::text")
            .get()
            .replace("(", "")
            .split(" ")[2]
        )

        item["rating"] = rating_map.get(
            book_details.css(".star-rating::attr(class)").get().split()[-1]
        )

        item["category"] = breadcrumb.css("li")[2].css("a::text").get()

        item["description"] = book_details.css(
            "div#product_description + p::text"
        ).get()

        item["upc"] = book_details.css("tr:contains('UPC') td::text").get()

        yield item
