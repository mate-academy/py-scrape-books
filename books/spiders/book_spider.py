from typing import Generator, Any

import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]:

        """
        Parse the main page and follow links to individual book pages.
        """
        books = response.css(".product_pod h3 a::attr(href)").getall()
        for book in books:
            absolute_url = response.urljoin(book)
            yield response.follow(absolute_url, callback=self.parse_book)

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response) -> Generator[dict[str, str | Any], Any, None]:
        """
        Parse individual book page and extract required information.
        """
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".availability::text").re_first(r"\d+"),
            "rating": self.get_book_rating(response),
            "category": response.css(".breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description ~ p::text").get(),
            "upc": response.css("table tr:nth-child(1) td::text").get(),
        }

    def get_book_rating(self, response) -> str:
        """
        Extract the book's rating by converting the class into a readable value.
        """
        ratings = {
            "One": "1",
            "Two": "2",
            "Three": "3",
            "Four": "4",
            "Five": "5",
        }
        rating_class = response.css(".star-rating").attrib.get("class", "")
        for word, number in ratings.items():
            if word in rating_class:
                return number
        return "0"
