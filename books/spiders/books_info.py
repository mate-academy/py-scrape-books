from typing import Generator

import scrapy


class BooksInfoSpider(scrapy.Spider):
    name = "books_info"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response, **kwargs) -> Generator[scrapy.Request]:
        for book in response.css(".product_pod"):
            detail_url = response.urljoin(book.css("h3 > a::attr(href)").get())
            yield scrapy.Request(
                detail_url,
                callback=self.parse_book_details,
                meta={"book_selector": book},
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response) -> dict:
        book = response.meta["book_selector"]

        return {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": int(
                response.css(".instock.availability::text")
                .getall()[1]
                .strip()
                .split()[2]
                .strip("(")
            ),
            "rating": self.parse_rating(
                book.css(".star-rating::attr(class)").get().split()[1]
            ),
            "category": response.css(".breadcrumb > li:nth-child(3) > a::text").get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("tr:contains('UPC') td::text").get(),
        }

    @staticmethod
    def parse_rating(rating: str) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_map[rating]
