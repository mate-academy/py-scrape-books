import scrapy
from scrapy.http import Response
from typing import Generator


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            book_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(book_url, self.parse_book_details)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book_details(response: Response) -> Generator:
        title = response.css(".product_main > h1::text").get()
        price = float(response.css(
            ".price_color::text"
        ).get().replace("£", ""))
        amount_in_stock = (
            response.css(".instock.availability::text").getall()[1].strip()
        )
        rating = (
            response.css(
                ".star-rating::attr(class)"
            ).get().replace("star-rating ", "")
        )
        category = response.css(
            "ul.breadcrumb > li:nth-child(3) > a::text"
        ).get()
        description = response.css("#product_description + p::text").get()
        upc = response.css("th:contains('UPC') + td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
