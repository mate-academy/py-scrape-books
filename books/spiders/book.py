import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css("div.image_container"):
            url = book.css("a::attr(href)").get()
            yield response.follow(url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book(book: Response) -> None:
        rating = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        yield {
            "title": book.css("div.col-sm-6 h1::text").get(),
            "price": float(book.css(
                "p.price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": int(
                book.css(
                    "p.availability"
                ).get().split()[-3].replace("(", "")
            ),
            "rating": rating[book.css(
                "p.star-rating"
            ).get().split()[2].replace('\">', "")],
            "category": book.css(".breadcrumb a::text").getall()[2],
            "description": book.css("p::text").getall()[10],
            "UPC": book.css(".table td::text").get()
        }
