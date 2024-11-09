import scrapy
from scrapy import Selector
from scrapy.http import Response
from enum import Enum

from books.items import BooksItem


class RatingEnum(Enum):
    Zero = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


def get_rating_value_from_class_names(class_names: str) -> int | None:
    class_names_list = class_names.split()
    rating_value_class = class_names_list[-1]
    return RatingEnum[rating_value_class].value


class BooksListSpider(scrapy.Spider):
    name = "books_list"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book_with_details(self, response: Response) -> None:
        book = BooksItem()
        book["title"] = response.meta["book_data"].css("a::attr(title)").get()
        book["price"] = float(response.meta["book_data"].css(
            ".price_color::text").get().replace("£", ""))
        book["rating"] = get_rating_value_from_class_names(
            response.meta["book_data"].css(".star-rating::attr(class)").get())
        book["category"] = response.css(
            ".breadcrumb li:nth-child(3) > a::text").get()
        book["description"] = response.css(
            "#product_description + p::text").get() or "No description"
        book["upc"] = response.css("table tr:first-child td::text").get()
        book["amount_in_stock"] = response.css(
            ".instock.availability::text").re_first(r"\((\d+) available\)")

        yield book

    def parse_book(self, book: Selector, response: Response) -> None:
        details_link = book.css("h3 > a::attr(href)").get()
        if details_link:
            yield response.follow(details_link,
                                  callback=self.parse_book_with_details,
                                  meta={"book_data": book})

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            yield from self.parse_book(book, response)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
