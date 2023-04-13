import scrapy

from scrapy.http import Response

from typing import Generator


RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def get_digits_from_string(arg: str) -> int:
        return int("".join([char for char in arg if char.isdigit()]))

    def parse_single_book(self, book: Response) -> Generator:
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(book.css(
                ".price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": self.get_digits_from_string(
                book.css("tr:nth-child(6) > td::text").get()
            ),
            "rating": RATINGS[book.css(
                "p.star-rating::attr(class)"
            ).get().split()[1]],
            "category": book.css(
                ".breadcrumb > li:nth-child(3) a::text"
            ).get(),
            "description": book.css("article > p::text").get(),
            "upc": book.css(".table tr:nth-child(1) td::text").get()

        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            book_page = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(book_page, callback=self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)
