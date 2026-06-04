from typing import Any, Generator

import scrapy
from scrapy.http import Response

from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(
        self,
        response: Response,
        **kwargs,
    ) -> Generator[scrapy.Request | ScrapeBooksItem, Any, None]:
        for book in response.css(".product_pod"):
            detail_url = response.urljoin(book.css("h3 a::attr(href)").get())
            raw_rating_class = book.css(".star-rating::attr(class)").get()
            rating_word = raw_rating_class.split()[-1] \
                if raw_rating_class else "Zero"

            yield response.follow(
                detail_url,
                callback=self._parse_detail,
                cb_kwargs={
                    "title": book.css("h3 a::attr(title)").get(),
                    "price": float(
                        book.css(".price_color::text").get().replace("£", "")
                    ),
                    "rating": self.rating_map.get(rating_word, 0),
                },
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detail(
        self,
        response: Response,
        title: str,
        price: float,
        rating: int,
    ) -> ScrapeBooksItem:
        in_stock_raw = response.css(".instock.availability::text").getall()
        in_stock = "".join(in_stock_raw).strip()
        in_stock = in_stock.replace(
            "In stock (", ""
        ).replace(
            " available)", ""
        ).strip()

        description = response.css(
            "#product_description + p::text"
        ).get(default="")

        category = response.css(
            ".breadcrumb li:nth-last-child(2) a::text"
        ).get(
            default=""
        )

        upc = response.css(".table tr:nth-child(1) td::text").get(default="")

        item = ScrapeBooksItem()
        item["title"] = title
        item["price"] = price
        item["rating"] = rating
        item["amount_in_stock"] = in_stock
        item["description"] = description
        item["category"] = category
        item["upc"] = upc

        return item
