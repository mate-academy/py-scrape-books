from typing import Generator

from scrapy.http import Response
import scrapy


RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book_page(book_page: Response) -> Generator:
        title = book_page.css(".product_main > h1::text").get()
        price = book_page.css(".price_color::text").get()[1:]
        amount = book_page.css(".instock").get().split()[7][1:]
        rating = book_page.css(".star-rating::attr(class)").get().split()[-1]
        category = book_page.css("li:nth-child(3) a::text").get()
        description = book_page.css("article > p::text").get()
        upc = book_page.css(".table tr td::text").get()

        yield {
            "title": title,
            "price": float(price),
            "amount_in_stock": int(amount),
            "rating": RATING[rating],
            "category": category,
            "description": description,
            "upc": upc
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            yield scrapy.Request(
                response.urljoin(book.css("h3 > a::attr(href)").get()),
                callback=self.parse_book_page
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )
