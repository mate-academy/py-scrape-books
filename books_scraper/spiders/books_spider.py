from typing import Any, Optional

import scrapy
from scrapy import Request
from scrapy.http import Response
from books_scraper.items import BooksScraperItem


class BooksSpiderSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs: Any) -> Optional[Request]:
        book_links = response.css("h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(link, self.parse_book)

        # Get the link to the next page, if available
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response) -> Optional[dict]:
        item = BooksScraperItem()

        # Extract book information and assign to item fields
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["amount_in_stock"] = response.css(
            "p.in_stock span::text").get().strip()
        item["rating"] = response.css(
            "p.star-rating::attr(class)").get().split(" ")[-1]
        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css(
            "meta[name=\'description\']::attr(content)").get()
        item["upc"] = response.css("table tr:nth-child(1) td::text").get()

        # Return the item for further processing
        yield item
