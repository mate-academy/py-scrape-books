import re
from typing import Generator

import scrapy
from scrapy import Request
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[Request]:
        for book in response.css("article.product_pod"):
            book_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(
                url=book_url,
                callback=self.parse_book,
                meta={
                    "title": book.css("h3 a::attr(title)").get(),
                    "price": book.css("p.price_color::text").get(),
                },
            )
        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> Generator[dict]:
        raw = response.xpath(
            "//th[text()='Availability']/following-sibling::td/text()"
        ).get()

        quantity = int(re.search(r"\d+", raw).group())
        yield {
            "title": response.meta["title"],
            "price": response.meta["price"],
            "amount_in_stock": quantity,
            "rating": response.css("p.star-rating::attr(class)")
            .get().split()[-1],
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text")
            .get(),
            "description": response.css("p.description::text").get(),
            "upc": response
            .xpath("//th[text()='UPC']/following-sibling::td/text()").get(),
        }
