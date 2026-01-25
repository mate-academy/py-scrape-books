import re
from typing import Iterator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Iterator[scrapy.Request]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for href in book_links:
            book_url = response.urljoin(href)
            yield scrapy.Request(
                url=book_url,
                callback=self.parse_book,
            )

        next_href = response.css("li.next a::attr(href)").get()
        if next_href:
            yield response.follow(
                next_href,
                callback=self.parse,
            )

    def parse_book(self, response: Response) -> Iterator[dict]:
        title = response.css(
            "div.product_main h1::text"
        ).get(default="").strip()

        price_text = response.css(
            "p.price_color::text"
        ).get(default="").strip()
        price = self._parse_price(price_text)

        stock_parts = response.css("p.availability::text").getall()
        stock_text = " ".join(part.strip() for part in stock_parts)
        amount_in_stock = self._parse_stock(stock_text)

        rating_class = response.css(
            "p.star-rating::attr(class)"
        ).get(default="")
        rating = self._parse_rating(rating_class)

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get(default="").strip()

        description = response.css("#product_description ~ p::text").get()
        if description:
            description = description.strip()
        else:
            description = ""

        upc = self._extract_table_value(response, "UPC")

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    @staticmethod
    def _parse_price(price_text: str) -> float:
        cleaned = price_text.replace("£", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_stock(stock_text: str) -> int:
        match = re.search(r"(\d+)\s+available", stock_text)
        if match:
            return int(match.group(1))
        return 0

    @staticmethod
    def _parse_rating(class_attr: str) -> int:
        mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        for name, value in mapping.items():
            if name in class_attr:
                return value

        return 0

    @staticmethod
    def _extract_table_value(
        response: Response,
        header: str,
    ) -> str:
        xpath = (
            "//table[contains(@class,'table-striped')]"
            f"//tr[th[normalize-space()='{header}']]/td/text()"
        )
        return response.xpath(xpath).get(default="").strip()
