import re
from typing import Generator

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response


RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        yield from response.follow_all(
            css="article.product_pod h3 a", callback=self.parse_book
        )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        return {
            "title": response.css("div.product_main h1::text").get(),
            "price": self._parse_price(response),
            "amount_in_stock": self._parse_amount_in_stock(response),
            "rating": self._parse_rating(response),
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": self._get_table_value(response, "UPC"),
        }

    @staticmethod
    def _parse_price(response: Response) -> float:
        price = response.css("div.product_main p.price_color::text").get()
        return float(price.replace("£", ""))

    @staticmethod
    def _parse_amount_in_stock(response: Response) -> int:
        availability = " ".join(
            response.css("div.product_main p.availability::text").getall()
        )
        match = re.search(r"\d+", availability)
        return int(match.group()) if match else 0

    @staticmethod
    def _parse_rating(response: Response) -> int:
        classes = response.css(
            "div.product_main p.star-rating::attr(class)"
        ).get()
        return RATINGS[classes.split()[-1]]

    @staticmethod
    def _get_table_value(response: Response, header: str) -> str:
        xpath = "//table//th[text()=$header]/following-sibling::td/text()"
        return response.xpath(xpath, header=header).get()


def main() -> None:
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "books.jl": {
                    "format": "jsonlines",
                    "encoding": "utf-8",
                    "mode": "overwrite",
                },
            },
            "ROBOTSTXT_OBEY": True,
            "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
            "DOWNLOAD_DELAY": 0.1,
            "LOG_LEVEL": "WARNING",
        }
    )
    process.crawl(BooksSpider)
    process.start()


if __name__ == "__main__":
    main()
