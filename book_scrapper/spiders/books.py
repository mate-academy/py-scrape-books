from typing import Any

import scrapy
from scrapy.http import Response

from book_scrapper.items import BookScrapperItem

STARS_MAP = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        for book in response.css("article.product_pod"):
            url = response.urljoin(book.css("a::attr(href)").get())
            yield scrapy.Request(url, callback=self._parse_book_info)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_info(self, response: Response) -> BookScrapperItem:
        book_item = BookScrapperItem()

        book_item["title"] = response.css("div.product_main > h1::text").get()
        book_item["price"] = response.css("p.price_color::text").get()[1:]
        book_item["amount_in_stock"] = (
            response.css("p.instock::text").getall()[1].strip().split()[-2][1:]
        )
        book_item["rating"] = STARS_MAP.get(
            response.css("p.star-rating::attr(class)").get().split()[-1]
        )
        book_item["category"] = response.css(
            "ul.breadcrumb > li:nth-child(3) a::text"
        ).get()
        book_item["description"] = response.css("article > p::text").get()
        book_item["upc"] = response.css(
            "table.table-striped tr:nth-child(1) td::text"
        ).get()

        return book_item
