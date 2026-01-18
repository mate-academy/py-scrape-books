import re
from typing import Any
from collections.abc import Generator

import scrapy
from scrapy import Request
from scrapy.http import Response
from pathlib import Path


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_detail_page(self, response: Response) -> Generator[
        dict[str, Any], None, None
    ]:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        rating_set = {"One", "Two", "Three", "Four", "Five"}

        classes_text = response.css(".star-rating::attr(class)").get()
        rating = 0
        if classes_text:
            classes_set = set(classes_text.split())
            rating_class_set = classes_set.intersection(rating_set)
            if rating_class_set:
                rating = rating_map[rating_class_set.pop()]

        text = "".join(response.css("p.availability::text").getall()).strip()
        match = re.search(r"\((\d+) available", text)
        amount_in_stock = int(match.group(1)) if match else 0

        yield {
            "title": response.css(".product_main").css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": response.css(".breadcrumb > li > a::text")[2].get(),
            "description": response.xpath(
                '//div[@id="product_description"]'
                '/following-sibling::p[1]/text()'  # noqa
            ).get(),
            "upc": response.xpath(
                '//table[contains(@class, "table-striped")]'
                '/tr[th/text()="UPC"]/td/text()'
            ).get(),
        }

    def parse(self, response: Response, **kwargs) -> Generator[
        Request, None, None
    ]:
        filename = "books.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        book_cards = response.css(".product_pod")
        links_to_detail_pages = [
            book_card.css("a::attr(href)").get() for book_card in book_cards
        ]
        link_to_next_page = response.css(".next > a::attr(href)").get()
        for link in links_to_detail_pages:
            absolute_url = response.urljoin(link)
            yield scrapy.Request(
                url=absolute_url, callback=self.parse_detail_page
            )

        if link_to_next_page is not None:
            yield response.follow(link_to_next_page, callback=self.parse)
