import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def calc_rating(rating: str) -> int:
        rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_dict[rating]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            book_url = response.urljoin(book.css("a::attr(href)").get())
            yield scrapy.Request(book_url, callback=self.parse_single_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_single_book(self, book: Response) -> None:
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(book.css(
                ".price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": book.css("tr:nth-child(6) > td::text").get(),
            "rating": self.calc_rating(
                book.css(".star-rating::attr(class)").get().split(" ")[1]
            ),
            "category": book.css(
                ".breadcrumb > li:nth-child(3) > a:nth-child(1)::text"
            ).get(),
            "description": book.css(
                ".product_page > p:nth-child(3)::text"
            ).get(),
            "UPC": book.css("tr:nth-child(1) > td::text").get(),
        }
