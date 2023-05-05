import scrapy
from scrapy.http import Response
from typing import Generator


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> Generator:
        book_links = response.css("h3 a::attr(href)").getall()
        yield from response.follow_all(book_links, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator:
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        title = response.css("h1::text").get()
        price = float(
            response.css("p.price_color::text").get().replace("£", "")
        )
        availability = int(
            response.css("p.availability::text").re_first(r"([\d]+) available")
        )
        rating_str = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating ([A-Za-z]+)"
        )
        rating = rating_map.get(rating_str, None)
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("div#product_description + p::text").get()
        upc = response.css("table tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": availability,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
