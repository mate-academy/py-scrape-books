import json
import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            next_page_url = response.urljoin(
                book.css(".product_pod h3 a::attr(href)").get()
            )
            yield response.follow(
                next_page_url, self.parse_book_details, meta={
                    "category_url": next_page_url
                }
            )

        next_page_link = response.css(".next a::attr(href)").get()
        if next_page_link:
            yield response.follow(next_page_link, self.parse)

    def parse_book_details(self, response: Response):

        book_info = {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".product_main .price_color::text").get(),
            "amount_in_stock": response.css(
                ".instock.availability::text").re_first(r"\d+"),
            "rating": response.css(
                ".product_main .star-rating::attr(class)"
            ).re_first(r"star-rating\s(.+)"),
            "category": response.css(".breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("tr:nth-of-type(1) td::text").get(),
        }

        with open("books.jl", "a") as f:
            f.write(json.dumps(book_info) + "\n")
        self.log("Saved book data to file")

        yield book_info
