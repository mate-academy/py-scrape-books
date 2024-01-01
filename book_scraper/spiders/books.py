import scrapy
from scrapy.http import Response
from book_scraper.items import BookScraperItem
from typing import Any, Generator


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[BookScraperItem, Any, None]:

        for book_link in response.css(".col-xs-6 h3 a"):
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css(".pager .next a")

        if next_page:
            yield response.follow(next_page[0], callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> BookScraperItem:
        book = response.css(".product_main")

        return BookScraperItem(
            title=book.css("h1::text").get(),
            price=float(book.css(".price_color::text").get()[1:]),
            amount_in_stock=int(book.css(".instock::text")[1].re(r"(\d+)")[0]),
            rating=book.css(".star-rating::attr(class)").get().split()[1],
            category=response.css(".breadcrumb li a::text").getall()[2],
            description=response.css("#product_description + p::text").get(),
            upc=response.css("table td::text").get(),
        )
