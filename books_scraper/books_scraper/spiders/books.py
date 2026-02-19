import scrapy
from scrapy.http import Response
from typing import Any, Generator

from books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[Any, None, None]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(
        self, response: Response, **kwargs
    ) -> Generator[Any, None, None]:
        item = BooksScraperItem()

        item["title"] = response.css(
            ".product_main h1::text"
        ).get()

        price_text = response.css(
            ".price_color::text"
        ).re_first(r"\d+\.\d+")

        stock_text = response.css(
            ".availability::text"
        ).re_first(r"\d+")

        rating_class = response.css(
            ".star-rating::attr(class)"
        ).get()

        rating_word = (
            rating_class.replace("star-rating ", "")
            if rating_class
            else None
        )

        item["price"] = float(price_text) if price_text else 0.0
        item["amount_in_stock"] = (
            int(stock_text) if stock_text else 0
        )
        item["rating"] = self.rating_map.get(rating_word, 0)

        item["category"] = response.xpath(
            "//ul[@class='breadcrumb']/li[last()-1]/a/text()"
        ).get() or ""

        description = response.css(
            "#product_description ~ p::text"
        ).get()

        item["description"] = (
            description.replace("...more", "").strip()
            if description
            else ""
        )

        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get() or ""

        yield item
