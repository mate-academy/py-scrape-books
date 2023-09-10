import scrapy
from scrapy import Request
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    @staticmethod
    def get_book_rating(score: str) -> int | str:
        ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return ratings.get(score, "There's no such rating")

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get().strip(),
            "price": float(
                response.css("p.price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.css("p.availability::text").re_first(
                r"\d+"
            ),
            "rating": self.get_book_rating(
                response.css("p.star-rating::attr(class)").get().split()[1]
            ),
            "number_of_reviews": response.css(
                "th:contains('Number of reviews') + td::text"
            ).get(),
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                "meta[name='description']::attr(content)"
            )
            .get()
            .strip(),
            "upc": response.css("th:contains('UPC') + td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> Request:
        for book_url in response.css("h3 a::attr(href)").extract():
            yield response.follow(book_url, self.parse_book)

        next_page = response.css("li.next a::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)
