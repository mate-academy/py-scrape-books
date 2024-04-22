import scrapy
from scrapy.http import Response

from books_lib.items import Book


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_detail_links = response.css(".product_pod > h3 > a")

        yield from response.follow_all(book_detail_links, self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _get_amount_in_stock(response: Response):
        response = response.css("table.table td::text").getall()[5]
        return int("".join(
            num
            for num in response
            if num.isnumeric()
        ))

    @staticmethod
    def _get_rating(response: Response):
        response = response.css("p.star-rating::attr(class)").get().split()[1]
        numbers = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return numbers.get(response)

    def parse_book(self, response: Response) -> Book:
        return Book(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css("p.price_color::text").get()[1:]),
            amount_in_stock=self._get_amount_in_stock(response),
            rating=self._get_rating(response),
            category=response.css(".breadcrumb > li > a::text").getall()[2],
            description=response.css(".product_page > p::text").get(),
            upc=response.css(".table td::text").getall()[0],
        )
