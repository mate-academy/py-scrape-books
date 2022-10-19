from word2number import w2n
from typing import Generator
import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_single_book(book: Response) -> Generator:
        description = book.css("#content_inner > article > p::text")\
            .get().encode("ascii", "ignore")
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(
                book.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int("".join(
                [number for number in book.css("tr:nth-child(6) > td::text")
                 .get()if number.isdigit()])),
            "rating": w2n.word_to_num(
                book.css("p.star-rating::attr(class)").get().split()[-1]),
            "category": book.css("ul > li:nth-child(3) > a::text").get(),
            "description": description.decode(),
            "upc": book.css("tr:nth-child(1) > td::text").get()
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".col-xs-6 > article > div > a::attr(href)")\
                .getall():
            yield scrapy.Request(response.urljoin(book),
                                 callback=self.parse_single_book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
