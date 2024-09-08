from typing import Generator

import scrapy
from scrapy.http import Response


STR_TO_INT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            book_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator[dict, None, None]:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css("p.availability::text").re_first(r'\d+')),
            "rating": self.get_rating(response),
            "category": response.css("ul.breadcrumb > li > a::text").getall()[-1],
            "description": response.css("article.product_page > p::text").get(),
            "upc": response.css("table.table tr:nth-child(1) td::text").get()
        }

    @staticmethod
    def get_rating(response: Response) -> int:
        rating = response.css("p.star-rating::attr(class)").get().split()[-1]
        return STR_TO_INT.get(rating, 0)
