import re
import scrapy
from scrapy.http import Response, Request
from typing import Iterator, Any


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Iterator[Request]:
        book_links = (
            response.css("article.product_pod h3 a::attr(href)")
            .getall()
        )
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_page)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(self, response: Response) -> Iterator[dict[str, Any]]:
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.replace(
            "star-rating ", ""
        ) if rating_class else None

        availability_text = response.xpath(
            "//th[text()='Availability']/following-sibling::td/text()"
        ).get()
        amount_in_stock = self._extract_stock_amount(availability_text)

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        }

    def _extract_stock_amount(self, text: str) -> int:
        if text:
            match = re.search(r"\d+", text)
            if match:
                return int(match.group())
        return 0
