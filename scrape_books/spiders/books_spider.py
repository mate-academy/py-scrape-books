import scrapy
from scrapy.http import Response


BOOK_RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css("article.product_pod"):
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_single_book(self, book: Response) -> dict:
        yield {
            "title": book.css(".row .product_main h1::text").get(),
            "price": float(book.css(".price_color::text").get()[1:]),
            "amount_in_stock": int(book.css("p.availability").get().split()[-3][1:]),
            "rating": BOOK_RATING[
                book.css("p.star-rating::attr(class)").get().split()[-1]
            ],
            "category": book.css(".breadcrumb a::text").getall()[-1],
            "description": book.css(".sub-header + p::text").get(),
            "upc": book.css("table.table-striped td::text").get(),
        }
