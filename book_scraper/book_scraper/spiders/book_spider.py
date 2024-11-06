import scrapy
from scrapy.http import Response, Request
from typing import Generator


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self, response: Response, **kwargs
    ) -> Generator[Request, None, None]:
        for category_link in response.css(
            ".side_categories ul li ul li a::attr(href)"
        ).getall():
            yield response.follow(category_link, self.parse_category)

    def parse_category(
            self, response: Response
    ) -> Generator[Request, None, None]:
        for book in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(book, self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_category)

    def parse_single_book(
            self, response: Response
    ) -> Generator[Request, None, None]:
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": response.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+) available\)"),
            "rating": rating_map[
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ],
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description": response.css("div#product_description + p::text")
            .get()
            .replace("\xa0", " "),
            "upc": response.css(
                ".table-striped tr:nth-child(1) td::text"
            ).get(),
        }
