import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail_page = book.css("h3 a::attr(href)").get()
            yield response.follow(
                url=detail_page, callback=self.parse_books_with_details
            )

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_books_with_details(book: Response) -> dict:

        yield {
            "title": book.css("h1::text").get(),
            "price": book.css(".price_color::text").get(),
            "amount_in_stock":
                book.css("p.availability").get().split()[-3].replace("(", ""),
            "rating": len(book.css(".star-rating::text").getall()),
            "category": (
                book.css(".breadcrumb > li:nth-last-child(2) > a::text").get()
            ),
            "description":
                book.css("#product_description + p::text").get().strip(),
            "upc": len(book.css("td::text").get()),
        }
