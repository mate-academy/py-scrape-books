import re

import scrapy
from scrapy.http import Response


class BookscrapingSpider(scrapy.Spider):
    name = "bookscraping"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):

        all_ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield {
            "title": response.css("h1::text").get(),
            "price": (
                float(
                    response.css("p.price_color::text")
                    .get(default="£0")
                    .replace("£", "")
                    .strip()
                )
                if response.css("p.price_color::text").get()
                else 0.0
            ),
            "amount_in_stock": (
                int(
                    re.search(
                        r"\d+",
                        response.xpath(
                            "//th[text()='Availability']/following-sibling::td/text()"
                        ).get(default="0"),
                    ).group()
                )
                if re.search(
                    r"\d+",
                    response.xpath(
                        "//th[text()='Availability']/following-sibling::td/text()"
                    ).get(default="0"),
                )
                else 0
            ),
            "rating": all_ratings.get(
                (
                    (
                        response.css("p.star-rating::attr(class)")
                        .get(default="")
                        .split()[-1]
                    )
                    if response.css("p.star-rating::attr(class)").get()
                    else ""
                ),
                0,
            ),
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        }
