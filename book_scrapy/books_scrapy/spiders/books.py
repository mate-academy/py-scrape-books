import scrapy
from scrapy.http import Response

from ..pipelines import take_description


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books_1/page-1.html"
    ]

    def parse_book_page(self, book: Response) -> dict:
        yield {
            "title": book.css(".product_main h1::text").get(),
            "price": book.css(".product_main p.price_color::text").get(),
            "amount_in_stock": book.xpath(
                "//th[text()='Availability']/following-sibling::td/text()"
            ).get(default=""),
            "rating(1-5)": book.css(
                "p.star-rating::attr(class)").get(default="").split()[-1],
            "category": book.css("ul.breadcrumb li a::text").getall(),
            "description": take_description(book),
            "upc": book.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(default=""),
        }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css("ol.row li"):
            book_link = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(book_link, callback=self.parse_book_page)
        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
