from typing import Any

import scrapy
from scrapy.http import Response

from books.items import BooksItem


def get_num_from_txt(word: str) -> int:
    word = word.lower()
    nums = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }
    return nums[word]


class BooksShopSpider(scrapy.Spider):
    name = "books-shop"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Any:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for link in book_links:
            yield response.follow(
                link,
                callback=self.parse_details,
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response: Response) -> Any:
        item = BooksItem()

        item["title"] = response.css("div.product_main h1::text").get()

        item["price"] = response.css("p.price_color::text").get()

        availability_text = response.css("p.availability::text").re_first(
            r"\d+")
        item["amount_in_stock"] = availability_text

        rating_class = response.css("p.star-rating::attr(class)").get()
        item["rating"] = get_num_from_txt(rating_class.split()[-1])

        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

        description = response.css(
            "#product_description ~ p::text"
        ).get()
        item["description"] = description

        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()

        yield item
