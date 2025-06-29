import scrapy
from scrapy.http import Response
from typing import Generator
from book_parser.items import BookParserItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(
            self, response: Response, **kwargs
    ) -> Generator[scrapy.Request | dict, None, None]:
        books = response.css("h3 > a::attr(href)").getall()
        for book in books:
            book_url = response.urljoin(book)
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator[dict, None, None]:
        item = BookParserItem()

        item["title"] = response.css("div.product_main > h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["amount_in_stock"] = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        item["rating"] = response.css(
            "p.star-rating"
        ).attrib["class"].split()[-1]
        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()
        item["description"] = response.css(
            "div#product_description ~ p::text"
        ).get()
        item["upc"] = response.css(
            "table.table.table-striped tr:nth-child(1) td::text"
        ).get()

        yield item
