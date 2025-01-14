from typing import Generator

import scrapy
from scrapy.http import Response
from word2number import w2n


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Generator:
        book_page_links = response.css("a[title]")
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_book(self, response: Response) -> Generator:

        yield {
            "title": response.css(".product_page h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+)\s"),
            "rating": w2n.word_to_num(
                response.css("p.star-rating").attrib["class"].split()[1]
            ),
            "category": response.css(
                ".breadcrumb > li a::text"
            ).getall()[2],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table-striped td::text").get()
        }
