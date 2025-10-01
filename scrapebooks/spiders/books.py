from typing import Any, Generator, Union

import scrapy
import re

from scrapebooks.items import ScrapebooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    RATING = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: scrapy.http.Response) -> Generator[Union[dict, Any], None, None]:
        for book in response.css("h3 a::attr(href)").getall():
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: scrapy.http.Response) -> Generator[dict | Any]:
        instock_text = " ".join(response.css("p.instock::text").getall()).strip()
        match = re.search(r"(\d+)", instock_text)
        amount_in_stock = int(match.group(1)) if match else 0

        rating_class = response.css("p.star-rating::attr(class)").get(default="")
        rating_word = rating_class.split()[-1] if rating_class else ""
        rating = self.RATING.get(rating_word, None)

        yield ScrapebooksItem(
            title=response.css("div.product_main h1::text").get(default="").strip(),
            price=response.css("p.price_color::text").get(default="").strip(),
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=response.xpath(
                "//ul[@class='breadcrumb']/li[3]/a/text()"
            ).get(default="").strip(),
            upc=response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(default="").strip(),
            description=response.css(
                "#product_description ~ p::text"
            ).get(default="").strip()
        )
