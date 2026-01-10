import re
from typing import Generator

import scrapy
from scrapy import Request
from scrapy.http import Response

from books_scrape.items import BooksScrapeItem


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
    def parse_book(response: Response) -> Generator[BooksScrapeItem]:
        raw = response.xpath(
            "//th[text()='Availability']/following-sibling::td/text()"
        ).get()

        quantity = 0
        if isinstance(raw, str):
            quantity = int(re.search(r"\d+", raw).group())

        rating = 0
        rating_response = response.css("p.star-rating::attr(class)").get()
        if rating_response is not None:
            rating = rating_response.split()[-1]

        yield BooksScrapeItem(
            title=response.meta["title"],
            price=response.meta["price"],
            amount_in_stock=quantity,
            rating=rating,
            category=response.css("ul.breadcrumb li:nth-child(3) a::text")
            .get(),
            description=response.xpath(
                "//div[@id='product_description']/"
                "following-sibling::p[1]/text()"
            ).get(default=""),
            upc=response
            .xpath("//th[text()='UPC']/following-sibling::td/text()").get(),
        )
