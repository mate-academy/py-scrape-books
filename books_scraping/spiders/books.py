from typing import Generator

import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def amount_in_stock(amount: str) -> int:
        return int("".join([number for number in amount if number.isdigit()]))

    def parse_book(self, response: Response) -> Generator:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": self.amount_in_stock(
                response.css("tr:nth-child(6) > td::text").get()
            ),
            "rating": w2n.word_to_num(
                response.css(".star-rating::attr(class)").get().split()[-1]
            ),
            "category": response.xpath("//div/div/ul/li[3]/a/text()").get(),
            "description": response.xpath("///article/p/text()").get(),
            "upc": response.css("tr:nth-child(1) > td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            book_url = response.urljoin(book.css("[title]::attr(href)").get())
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
