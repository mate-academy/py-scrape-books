import scrapy
from typing import Any
from scrapy.http import Response
from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    """Scrape books from https://books.toscrape.com/"""

    name = "books_spider"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any) -> None:
        """
        Parse the given response and yields book pages and pagination links
        """
        book_page_links = response.css("div.image_container a::attr(href)")
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_book(self, response: Response) -> None:
        """Parse book page"""
        book = ScrapeBooksItem()
        book["title"] = response.css(".product_main h1::text").get()
        book["price"] = float(
            response.css(".price_color::text")
            .get()
            .replace("£", "")
        )
        book["amount_in_stock"] = int(
            response.css(".instock.availability::text")
            .getall()[1]
            .split()[2]
            .replace("(", "")
        )
        rating = response.css(".star-rating::attr(class)").get().split()[-1]
        book["rating"] = self.rating_to_int(rating)
        book["category"] = response.css(".breadcrumb li a::text").getall()[-1]
        book["description"] = response.css("p::text").getall()[10]
        book["upc"] = response.css(".table.table-striped td::text").get()

        yield book

    @staticmethod
    def rating_to_int(rating: str) -> int:
        """Convert rating to integer"""
        try:
            return {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5
            }[rating]
        except KeyError:
            return 0
