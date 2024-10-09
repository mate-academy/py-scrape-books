from typing import Iterable, Dict

import scrapy
from scrapy.http import Response

BOOK_LIST_CSS = "li.col-xs-6"
NEXT_PAGE_CSS = "li.next a::attr(href)"
TITLE_CSS = "div.col-sm-6 h1::text"
PRICE_CSS = "div.col-sm-6 p.price_color::text"
AMOUNT_CSS = "div.col-sm-6 p.instock *::text"
RATING_CSS = "div.col-sm-6 p.star-rating::attr(class)"
CATEGORY_CSS = "ul.breadcrumb li" # response.css("ul.breadcrumb li:nth-child(3) a::text").get()
DESCRIPTION_CSS = "article.product_page p::text"
UPC_CSS = "table.table tr" # response.css("table.table tr:nth-child(1) td::text").get()


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css(BOOK_LIST_CSS):
            detail_page = book.css(
                "h3 a::attr(href)"
            ).get()
            yield response.follow(
                detail_page, callback=self.parse_book
            )

        next_page = response.css(
            NEXT_PAGE_CSS
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Iterable[Dict]:
        yield {
            "title": response.css(TITLE_CSS).get(),
            "price": float(
                response.css(
                    PRICE_CSS
                ).get().replace("£", "")
            ),
            "amount_in_stock": int("".join(
                response.css(AMOUNT_CSS).getall()
            ).strip().split("(")[1].split()[0]),
            "rating": self._word_to_number(
                response.css(
                    RATING_CSS
                ).get().split()[1]
            ),
            "category": response.css(
                CATEGORY_CSS
            ).getall()[2].split('html">')[1].split("</a")[0],
            "description": response.css(
                DESCRIPTION_CSS
            ).getall()[10],
            "upc": response.css(
                UPC_CSS
            ).getall()[0].split("td>")[1].split("<")[0]
        }

    def _word_to_number(self, word: str) -> int:
        words_to_digits = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10
        }
        return words_to_digits.get(word.lower(), -1)
