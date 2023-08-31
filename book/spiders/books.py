import scrapy
from scrapy.http.response import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: dict) -> None:
        for book in response.css(".product_pod"):
            book_page = response.urljoin(
                book.css(".product_pod h3 a::attr(href)").get()
            )
            yield scrapy.Request(book_page, callback=self.parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_single_book(book_page: Response) -> dict[str, str]:
        detail_info = {
            "title": book_page.css(".product_main > h1::text").get(),
            "price": book_page.css(".price_color::text").get(),
            "amount_in_stock": (
                book_page.css("tr:nth-child(6) > td::text").get()
                .replace("(", "")
                .split(" ")[2]
            ),
            "rating": (
                book_page.css("p.star-rating::attr(class)").get()
                .split()[1]
            ),
            "category": (
                book_page.css(".breadcrumb > li:nth-child(3) a::text").get()
            ),
            "description": book_page.css("article > p::text").get(),
            "upc": book_page.css(".table tr:nth-child(1) td::text").get(),
        }

        yield detail_info
