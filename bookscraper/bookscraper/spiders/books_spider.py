from __future__ import annotations

from typing import Any, Generator
import re

import scrapy
from scrapy.http import Response

from bookscraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name: str = "books"
    allowed_domains: list[str] = ["books.toscrape.com"]
    start_urls: list[str] = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        category_links: list[str] = response.css(
            "div.side_categories ul.nav-list ul li a::attr(href)"
        ).getall()
        for cat_link in category_links:
            full_url: str = response.urljoin(cat_link)
            yield scrapy.Request(full_url, callback=self.parse_category)

    def parse_category(
        self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        book_links: list[str] = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()
        for book_link in book_links:
            book_url: str = response.urljoin(book_link)
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page: str | None = response.css("li.next a::attr(href)").get()
        if next_page:
            next_url: str = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse_category)

    def parse_book(self, response: Response) -> Generator[BookItem, None, None]:
        item = BookItem()

        item["title"] = response.css("div.product_main h1::text").get()

        raw_price: str | None = response.css(
            "div.product_main p.price_color::text"
        ).get()
        item["price"] = raw_price.strip() if raw_price else None

        stock_text: str | None = response.css(
            "div.product_main p.instock.availability::text"
        ).re_first(r"(\d+)")
        item["amount_in_stock"] = int(stock_text) if stock_text else 0

        rating_classes: str | None = response.css(
            "div.product_main p.star-rating::attr(class)"
        ).get()
        if rating_classes:
            rating_str: str = rating_classes.replace("star-rating", "").strip()
            item["rating"] = rating_str
        else:
            item["rating"] = None

        breadcrumb_items: list[str] = response.css(
            "ul.breadcrumb li a::text"
        ).getall()
        item["category"] = (
            breadcrumb_items[2].strip() if len(breadcrumb_items) > 2 else None
        )

        description: str | None = response.css(
            "#product_description ~ p::text"
        ).get()
        item["description"] = description.strip() if description else None

        table_rows = response.css("table.table.table-striped tr")
        upc_code: str | None = None
        for row in table_rows:
            table_header: str | None = row.xpath("th/text()").get()
            if table_header == "UPC":
                upc_code = row.xpath("td/text()").get()
                break
        item["upc"] = upc_code

        yield item
