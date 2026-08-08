import re
from typing import Any

import scrapy
from scrapy.http import Response

from book_to_scrape.items import BookToScrapeItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any):
        for product in response.css(".product_pod"):
            book_url = product.css("h3 a::attr(href)").get()

            if not book_url:
                continue

            yield response.follow(
                response.urljoin(book_url),
                callback=self.parse_book,
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                response.urljoin(next_page),
                callback=self.parse,
            )

    def parse_book(self, response: Response):
        title = response.css("div.product_main h1::text").get() or ""

        price = response.css(".price_color::text").get() or ""
        price = price.replace("£", "").strip()

        rating_class = (
                response.css(".star-rating::attr(class)").get()
                or ""
        )
        rating_parts = rating_class.split()
        rating = rating_parts[1] if len(rating_parts) > 1 else ""

        description = (
                response.css("#product_description + p::text").get()
                or ""
        )

        breadcrumbs = response.css(".breadcrumb li a::text").getall()
        category = breadcrumbs[2].strip() if len(breadcrumbs) > 2 else ""

        availability = " ".join(
            text.strip()
            for text in response.css(
                "p.instock.availability::text"
            ).getall()
            if text.strip()
        )

        stock_match = re.search(r"\d+", availability)
        amount_in_stock = int(stock_match.group()) if stock_match else 0

        upc = (
                response.xpath(
                    '//th[text()="UPC"]/following-sibling::td/text()'
                ).get()
                or ""
        )

        yield BookToScrapeItem(
            title=title.strip(),
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description.strip(),
            upc=upc.strip(),
        )
