from collections.abc import Generator

import scrapy
from scrapy.http import Response

from book_scraper.items import BookScraperItem


RATING_VALUES = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self,
            response: Response
    ) -> Generator[scrapy.Request, None, None]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for book_link in book_links:
            yield response.follow(
                book_link,
                callback=self.parse_book,
            )

        next_page = response.css(
            "li.next a::attr(href)"
        ).get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(
            self,
            response: Response
    ) -> Generator[BookScraperItem, None, None]:
        price_text = response.css(
            "p.price_color::text"
        ).get(default="")
        stock_text = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        rating_class = response.css(
            "p.star-rating::attr(class)"
        ).get(default="")
        categories = response.css(
            "ul.breadcrumb li a::text"
        ).getall()
        rating_name = rating_class.split()[-1]

        yield BookScraperItem(
            title=response.css(
                "div.product_main h1::text"
            ).get(default=""),
            price=float(price_text.removeprefix("£")),
            amount_in_stock=(
                int(stock_text)
                if stock_text is not None
                else 0
            ),
            rating=RATING_VALUES[rating_name],
            category=categories[-1] if categories else "",
            description=response.css(
                "#product_description + p::text"
            ).get(default=""),
            upc=response.xpath(
                '//th[text()="UPC"]'
                "/following-sibling::td/text()"
            ).get(default=""),
        )
