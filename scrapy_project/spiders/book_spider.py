import re

import scrapy
from scrapy.http import Response


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        for book in response.css(".product_pod"):
            detail_url = book.css("h3 a::attr(href)").get()
            detail_url = response.urljoin(detail_url)

            yield scrapy.Request(
                detail_url,
                callback=self.parse_book_details
            )

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(
                next_page,
                callback=self.parse
            )

    def parse_book_details(self, response: Response) -> dict:
        availability_text = response.xpath(
            "//p[contains(@class, 'instock availability')]//text()"
        ).getall()
        availability_text = "".join(availability_text).strip()
        match = re.search(r"\d+", availability_text)
        available_count = int(match.group(0)) if match else 0

        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(
                response
                .css(".price_color::text")
                .get()
                .replace("£", "")
                .strip()
            ),
            "amount_in_stock": available_count,
            "rating": response
            .css("p.star-rating::attr(class)")
            .get()
            .split()[1],
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response
            .css("#product_description + p::text")
            .get(),
            "upc": response.css("th:contains('UPC') + td::text").get(),
        }
