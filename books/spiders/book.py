from typing import Any

import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> Any:
        books = response.css(".product_pod")

        for book in books:
            details_href = book.css("a[title]::attr(href)").get()
            yield response.follow(
                details_href, callback=self._get_book_details
            )

        next_page_href = response.css(".next a::attr(href)").get()

        if next_page_href:
            yield response.follow(next_page_href, callback=self.parse)

    @staticmethod
    def _get_book_details(response: Response) -> dict:
        title = response.css(".product_main > h1::text").get()
        price = float(
            response.xpath(
                "//th[text()='Price (incl. tax)']"
                "/following-sibling::td//text()"
            ).get().replace("£", "")
        )
        amount_in_stock = int(
            response.css(".availability::text").re_first(r"\d+")
        )
        rating = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}.get(
            response.css(
                ".star-rating::attr(class)"
            ).get().split()[-1].lower(),
            0
        )
        category = response.css(
            ".breadcrumb li:nth-last-child(2) a::text"
        ).get().lower()
        description = response.css("#product_description + p::text").get()
        upc = response.xpath(
            "//th[text()='UPC']/following-sibling::td//text()"
        ).get()

        return dict(
            title=title,
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc
        )
