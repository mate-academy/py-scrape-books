from typing import Generator, Union

import scrapy

from books_scraper.items import BooksScraperItem
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]
    base_url = "https://books.toscrape.com/catalogue/"
    custom_settings = {
        "FEEDS": {
            "books.jl": {
                "format": "jl",
                "overwrite": True
            },
        }
    }

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Generator[Union[scrapy.Request, BooksScraperItem], None, None]:
        for book in response.css("article.product_pod h3 a"):   # type: ignore
            link = book.attrib["href"]
            full_link = response.urljoin(link)
            yield scrapy.Request(full_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_book(
            response: Response
    ) -> Generator[BooksScraperItem, None, None]:
        item = BooksScraperItem()

        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = response.css("p.price_color::text").get()

        available = response.css("p.availability::text").re_first(r"\d+")
        item["amount_in_stock"] = int(available) if available else 0

        rating = response.css("p.star-rating::attr(class)").get()
        item["rating"] = rating.split()[-1] if rating else "Unknown"

        category = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = category[-1] if category else "Unknown"

        description = response.css("div#product_description ~ p::text").get()
        item["description"] = description.strip() if description else ""

        table = response.css("table.table.table-striped tr")
        for row in table:   # type: ignore
            heading = row.css("th::text").get()
            if heading == "UPC":
                item["upc"] = row.css("td::text").get()
                break

        yield item
