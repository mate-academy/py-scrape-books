import scrapy
from scrapy.http import HtmlResponse
from word2number import w2n

from ..items import BooksScrapperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/",
    ]

    def parse(self, response: HtmlResponse, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(
                url=response.urljoin(book_url), callback=self.parse_book
            )

        next_page_link = response.css("li.next a::attr(href)").get()
        if next_page_link is not None:
            yield scrapy.Request(
                url=response.urljoin(next_page_link), callback=self.parse
            )

    def parse_book(self, response: HtmlResponse):
        book_info = BooksScrapperItem()

        book_info["title"] = response.css("h1::text").get()
        book_info["price"] = float(
            response.css("p.price_color::text").get().replace("£", "")
        )
        book_info["amount_in_stock"] = int(
            response.css(".instock.availability::text").re_first(r"\d+")
        )
        book_info["rating"] = w2n.word_to_num(
            response.css("p.star-rating::attr(class)").get().split()[1]
        )
        book_info["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()
        book_info["description"] = response.css("article.product_page > p::text").get()
        book_info["upc"] = response.css(
            "table.table.table-striped tr:nth-child(1) td::text"
        ).get()

        yield book_info
