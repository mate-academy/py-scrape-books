import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        books_links = response.css("h3 > a::attr(href)").getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_book_page)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_amount_available(string: str) -> int:
        number = ""
        for symbol in string.strip():
            if symbol.isdigit():
                number += symbol
        return int(number)

    @staticmethod
    def get_rating_from_string(string: str) -> int:
        ratings = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        str_number = string.split()[-1]
        return ratings[str_number]

    def parse_book_page(self, response: Response) -> dict:
        title = response.css("h1::text").get()
        price = float(response.css(
            ".price_color::text"
        ).get().replace("£", ""))
        amount_in_stock = self.get_amount_available(
            response.css("td::text")[5].get()
        )
        rating = self.get_rating_from_string(
            response.css("p.star-rating::attr(class)").get()
        )
        category = response.css(
            ".breadcrumb > li:nth-child(3) > a::text"
        ).get()
        description = response.css(".product_page > p::text").get()
        upc = response.css("td::text")[0].get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
