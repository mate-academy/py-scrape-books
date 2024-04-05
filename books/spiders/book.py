import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_single_book)

        next_page_url = response.css(".next > a::attr(href)").get()
        print(next_page_url)

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def parse_single_book(book: Response):
        rate = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        yield BooksItem(
            title=book.css("h1::text").get(),
            price=float(book.css(".price_color::text").get().replace("£", "")),
            amount_in_stock=int(
                book.css(".availability").get().split()[-3].replace("(", "")
            ),
            rating=rate[book.css(
                ".star-rating::attr(class)"
            ).get().split()[-1]],
            category=book.css(".breadcrumb > li > a::text").getall()[-1],
            description=book.css(".product_page > p::text").get(),
            upc=book.css(".table > tr").css("td::text").get()
        )
