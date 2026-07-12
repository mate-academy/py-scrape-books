from typing import Iterable

import scrapy
from scrapy.http import Response, Request

from scrape_books.items import ScrapeBooksItem


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
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response) -> Iterable[Request]:
        category_urls = response.css(
            "ul.nav-list ul li a::attr(href)"
        ).getall()
        for url in category_urls:
            yield response.follow(url, self.parse_category)

    def parse_category(self, response: Response) -> Iterable[Request]:
        book_urls = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()
        for book_url in book_urls:
            yield response.follow(book_url, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_category)

    def parse_book(self, response: Response) -> ScrapeBooksItem:
        title = response.css("div.product_main h1::text").get()
        price = response.css("p.price_color::text").get()
        price = float(price.replace("£", ""))

        stock = response.css("p.instock.availability::text").re_first(r"\d+")
        if stock:
            stock = int(stock)

        rating = response.css("p.star-rating::attr(class)").get()
        rating = RATING_MAP[rating.split()[-1]]

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get()

        upc = response.css(
            "table.table-striped tr:nth-child(1) td::text"
        ).get()

        book = ScrapeBooksItem(
            title=title,
            price=price,
            amount_in_stock=stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc,
        )

        yield book
