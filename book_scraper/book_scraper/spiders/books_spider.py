import re
from collections.abc import Generator

import scrapy
from ..items import BookScraperItem
from scrapy.http import Response


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
        self,
        response: Response,
    ) -> Generator[scrapy.Request, None, None]:
        for url in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> BookScraperItem:
        amount_text = " ".join(
            response.css(".product_main .availability::text").getall()
        )
        amount = re.search(r"\d+", amount_text).group()

        rating_class = response.css(
            ".product_main .star-rating::attr(class)"
        ).get()
        rating_name = rating_class.split()[-1]

        return BookScraperItem(
            title=response.css("h1::text").get(""),
            price=response.css(".product_main .price_color::text").get(""),
            amount_in_stock=int(amount),
            rating=self.rating_map[rating_name],
            category=response.css(
                ".breadcrumb li:nth-last-child(2) a::text"
            ).get(""),
            description=response.css("#product_description + p::text")
            .get(""),
            upc=response.xpath(
                '//th[text()="UPC"]/following-sibling::td/text()'
            ).get(""),
        )
