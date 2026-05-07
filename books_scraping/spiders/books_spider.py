from enum import Enum
from typing import Generator

import scrapy
from scrapy.http import Response

HOME_URL = "https://books.toscrape.com/"


class Rating(Enum):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


class BooksSpider(scrapy.Spider):
    name = "books"  # CMD scrapy crawl books
    start_urls = [HOME_URL]

    def parse(self, response: Response, **kwargs) -> Generator:
        all_categories = response.css(".side_categories a")[1:]
        for category in all_categories:
            category_name = category.css("::text").get().strip()
            category_url = category.css("::attr(href)").get()

            # Pass category name to next callback
            yield response.follow(
                category_url,
                callback=self.parse_category,
                meta={"category": category_name},
            )

    def parse_category(self, response: Response) -> Generator:
        # Get category from previous page
        category = response.meta["category"]
        # Get all books in this category
        books = response.css(".product_pod")
        for book in books:
            title = book.css("h3 a::attr(title)").get()
            price = float(
                book.css(".price_color::text").get().replace("£", "")
            )
            book_url = book.css("h3 a::attr(href)").get()

            # Pass both category AND book info to next callback
            yield response.follow(
                book_url,
                callback=self.parse_book,
                meta={"category": category, "title": title, "price": price},
            )

        # Follow next page, keeping category context
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category,
                meta={"category": category},
            )

    def parse_book(self, response: Response) -> Generator:
        # Get everything from meta
        category = response.meta["category"]
        title = response.meta["title"]
        price = response.meta["price"]

        # Scrape additional details from this page
        description_parts = response.css(
            "#product_description ~ p::text"
        ).getall()
        description = " ".join(part.strip() for part in description_parts)
        amount_in_stock = int(
            response.xpath(".//p[contains(@class, 'availability')]/text()").re(
                r"(\d+)"
            )[0]
        )

        rating = self._format_rating(
            response.xpath(".//p[contains(@class, 'star-rating')]/@class")
            .get()
            .split()[1]
        )

        upc = response.xpath(
            "//th[contains(., 'UPC')]/following-sibling::td/text()"
        ).get()

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
    def _format_rating(score: str) -> int:
        try:
            rating = Rating[score].value
        except KeyError:
            return 0
        else:
            return rating
