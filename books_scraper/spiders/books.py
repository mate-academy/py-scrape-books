"""Spider that collects every book from books.toscrape.com."""

import re
from collections.abc import Generator

import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    """Scrape all catalogue pages and their book detail pages."""

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self,
            response: Response,
            **kwargs: object
    ) -> Generator[scrapy.Request, None, None]:
        """Follow every book link and continue through the catalogue."""
        for book_url in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(
            self,
            response: Response
    ) -> Generator[dict[str, object], None, None]:
        """Extract the required fields from one book detail page."""
        availability = " ".join(
            response.css("p.instock.availability::text").getall()
        )
        amount_match = re.search(r"\d+", availability)
        rating_classes = response.css(
            "p.star-rating::attr(class)"
        ).get(default="").split()
        breadcrumb_links = response.css(
            "ul.breadcrumb li a::text"
        ).getall()

        yield {
            "title": response.css(
                "div.product_main h1::text"
            ).get(default="").strip(),
            "price": response.css(
                "div.product_main p.price_color::text"
            ).get(default="").strip(),
            "amount_in_stock": (
                int(amount_match.group()) if amount_match else 0
            ),
            "rating": rating_classes[-1] if rating_classes else "",
            "category": (
                breadcrumb_links[-1].strip() if breadcrumb_links else ""
            ),
            "description": response.css(
                "#product_description + p::text"
            ).get(default="").strip(),
            "upc": response.xpath(
                "//th[normalize-space()='UPC']/following-sibling::td/text()"
            ).get(default="").strip(),
        }
