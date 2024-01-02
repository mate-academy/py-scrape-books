import scrapy
from scrapy.http import Response

from books.items import BookItem


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book(book: Response) -> BookItem:

        return BookItem(
            title=book.css("h1::text").get(),
            price=book.css(".price_color::text").get(),
            amount_in_stock=book.css(".instock").get().split()[7][1:],
            rating=book.css(".star-rating::attr(class)").get().split()[1],
            category=book.css(".breadcrumb li a::text").getall()[2],
            description=book.css(".product_page > p::text").get(),
            upc=book.css(".table tr td::text").get()
        )

    def parse(self, response: Response, **kwargs) -> Response:

        for book in response.css(".product_pod"):
            book_link = book.css("h3 a::attr(href)").get()
            book_link = response.urljoin(book_link)
            yield response.follow(url=book_link, callback=self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)
