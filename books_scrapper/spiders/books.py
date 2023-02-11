import scrapy
from scrapy.http import Response


class BookScraperSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_books(book: Response) -> dict:
        """
        Parse book detail page and yield ("title",
        "price", "amount_in_stock", "rating", "category",
        "description", "upc") of the book

        :param book: http response of detail book page
        """
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": book.css(".price_color::text").get(),
            "amount_in_stock": int(
                book.css(".instock.availability").get().split()[-3][1:]
            ),
            "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
            "category": book.css("li:nth-child(3) a::text").get(),
            "description": book.css("article > p::text").get(),
            "upc": book.css(".table tr td::text").get()
        }

    def parse(self, response: Response, **kwargs) -> dict:
        """
        Parse all book from "https://books.toscrape.com/"
        and yield detail info about each book

        :param response: http response of book page list
        :param kwargs: kwargs
        """
        for book in response.css(".product_pod").css("h3 a::attr(href)"):
            yield scrapy.Request(
                response.urljoin(book.get()),
                callback=self.parse_books
            )
        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)
