import re

import  scrapy
from scrapy.http import Response

from library.items import LibraryItem

RATING_MAP = {
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

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            item = LibraryItem(
                title=book.css("a::attr(title)").get(),
                price=float(book.css(".price_color::text").get().replace("£", "")),
                rating=RATING_MAP.get(
                    book.css("p.star-rating::attr(class)").get().replace("star-rating", "").strip()
                )
            )

            detail_url = response.urljoin(book.css("a::attr(href)").get())
            yield response.follow(
                detail_url,
                callback=self.parse_book_detail,
                meta={"item": item},
            )

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response: Response, **kwargs):
        item = response.meta["item"]

        item["category"] = response.css(
            "ul.breadcrumb li"
        )[-2].css("a::text").get()
        item["description"] = response.css(
            "#product_description + p::text"
        ).get()
        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()

        availability_text = response.xpath(
            "//th[text()='Availability']/following-sibling::td/text()"
        ).get()
        match = re.search(r"\((\d+) available\)", availability_text or "")
        item["amount_in_stock"] = int(match.group(1)) if match else 0

        yield item
