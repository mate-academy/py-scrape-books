import re
from typing import Generator, Optional
import scrapy
from scrapy.http import Response
from book_scraper.items import BookScraperItem


class BooksSpider(scrapy.Spider):
    name: str = "books"
    allowed_domains: list[str] = ["books.toscrape.com"]
    start_urls: list[str] = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        book_links: list[str] = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book_page)

        next_page: Optional[str] = response.css(
            "li.next a::attr(href)"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(
        self, response: Response
    ) -> Generator[BookScraperItem, None, None]:
        rating_class: Optional[str] = response.css(
            "p.star-rating::attr(class)"
        ).get()
        rating: Optional[str] = (
            rating_class.replace("star-rating ", "")
            if rating_class
            else None
        )

        availability_text: Optional[str] = response.xpath(
            '//th[text()="Availability"]/following-sibling::td/text()'
        ).get()
        amount_in_stock: int = self._extract_stock_amount(
            availability_text
        )

        item: BookScraperItem = BookScraperItem()
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["amount_in_stock"] = amount_in_stock
        item["rating"] = rating
        item["category"] = response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get()
        item["description"] = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).get()
        item["upc"] = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        yield item

    def _extract_stock_amount(self, text: Optional[str]) -> int:
        if text:
            match: Optional[re.Match[str]] = re.search(r"\d+", text)
            if match:
                return int(match.group())
        return 0
