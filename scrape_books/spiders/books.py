import scrapy
from scrapy.http import Response
from word2number import w2n
from typing import Generator


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    @staticmethod
    def amount_in_stock(amount: str) -> str:
        return "".join([number for number in amount if number.isdigit()])

    def parse_single_book(self, response: Response) -> Generator:
        book = response.css(".product_page")
        yield {
            "title": book.css("div.col-sm-6.product_main > h1::text").get(),
            "price": float(book.css("p.price_color::text").get()[1::]),
            "amount_in_stock": int(
                self.amount_in_stock(
                    book.css("tr:nth-child(6) > td::text").get()
                )
            ),
            "rating": w2n.word_to_num(
                book.css(".star-rating::attr(class)").get().split()[-1]
            ),
            "category": book.xpath("//div/div/ul/li[3]/a/text()").get(),
            "description": book.xpath("///article/p/text()").get(),
            "upc": book.css("tr:nth-child(1) > td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            url = response.urljoin(
                book.css("div.image_container > a::attr(href)").get()
            )
            yield scrapy.Request(url, callback=self.parse_single_book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
