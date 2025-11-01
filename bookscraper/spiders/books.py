from __future__ import annotations

import re
from typing import Iterable, Optional

import scrapy
from scrapy.http import Response

from bookscraper.items import BookItem


class BooksSpider(scrapy.Spider):
    """
    Single spider to scrape all 1000 books.

    Flow:
    - start at homepage
    - follow each category
    - paginate category pages
    - open each book detail and extract fields
    """

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # ---------- Top-level parse methods ----------

    def parse(self, response: Response) -> Iterable[scrapy.Request]:
        """Parse homepage and enqueue category pages."""
        category_links = response.css(
            ".side_categories ul li ul li a::attr(href)"
        ).getall()
        for href in category_links:
            url = response.urljoin(href)
            yield response.follow(url, callback=self.parse_category)

    def parse_category(self, response: Response) -> Iterable[scrapy.Request]:
        """
        Parse one category listing page:
        - Follow book detail links
        - Follow pagination "next"
        """
        # Book links
        for href in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            url = response.urljoin(href)
            # Normalize possible '../' by letting Scrapy resolve
            yield response.follow(url, callback=self.parse_book)

        # Pagination
        next_href = response.css("li.next a::attr(href)").get()
        if next_href:
            yield response.follow(next_href, callback=self.parse_category)

    # ---------- Detail page parsing ----------

    def parse_book(self, response: Response) -> BookItem:
        """Extract all required fields from the product detail page."""
        title = self._extract_first(
            response.css("div.product_main h1::text").get()
        )
        price_raw = self._extract_first(
            response.css("p.price_color::text"
                         ).get())
        availability_text = self._extract_first(
            response.css("p.availability::text"
                         ).getall())
        rating_raw = self._extract_first(
            response.css("p.star-rating").attrib.get("class", "")
        )
        category = self._extract_first(
            response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        )
        description = self._extract_description(response)
        upc = self._extract_table_value(response, "UPC")

        item: BookItem = {
            "title": title or "",
            "price": self._parse_price(price_raw),
            "amount_in_stock": self._parse_amount_in_stock(availability_text),
            "rating": self._extract_rating(rating_raw),
            "category": category or "",
            "description": description or "",
            "upc": upc or "",
        }
        return item

    # ---------- Helpers (DRY) ----------

    @staticmethod
    def _extract_first(value: Optional[str | list[str]]) -> Optional[str]:
        """Return first trimmed string from value or None."""
        if value is None:
            return None
        if isinstance(value, list):
            for candidate in value:
                candidate = (candidate or "").strip()
                if candidate:
                    return candidate
            return None
        return value.strip()

    @staticmethod
    def _extract_table_value(response: Response, header: str) -> Optional[str]:
        """Get table cell text by header label in the product info table."""
        xpath = (
            f'//table[contains(@class, "table")]'
            f'/tr[th[normalize-space()="{header}"]]/td/text()'
        )
        return BooksSpider._extract_first(response.xpath(xpath).get())

    @staticmethod
    def _extract_description(response: Response) -> Optional[str]:
        """
        The description is the first <p> after <h2 id="product_description">.
        Some books do not have a description; return empty string in that case.
        """
        text = response.xpath(
            '//h2[@id="product_description"]/following-sibling::p[1]/text()'
        ).get()
        return text.strip() if text else ""

    @staticmethod
    def _parse_price(text: Optional[str]) -> float:
        """Parse price like '£51.77' -> 51.77;
        return 0.0 if missing/invalid."""
        if not text:
            return 0.0
        # Keep digits and dot only
        cleaned = re.sub(r"[^\d.]", "", text)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_amount_in_stock(text: Optional[str]) -> int:
        """
        Parse availability like 'In stock (22 available)' -> 22.
        If no explicit count, assume 0.
        """
        if not text:
            return 0
        # text sometimes contains whitespace/newlines; compress it
        compact = " ".join(text.split())
        availability_match = re.search(
            r"\((\d+)\s+available\)",
            compact,
            flags=re.IGNORECASE
        )
        return int(availability_match.group(1)) if availability_match else 0

    @staticmethod
    def _extract_rating(class_attr: Optional[str]) -> int:
        """
        Map 'star-rating Three' -> 3.
        Classes include: One, Two, Three, Four, Five.
        """
        if not class_attr:
            return 0
        parts = class_attr.split()
        # Find the capitalized rating word
        word = next((p for p in parts if p.istitle()), "")
        mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return mapping.get(word, 0)
