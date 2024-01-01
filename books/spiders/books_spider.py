import scrapy
from scrapy.http import Response

from books.utils import get_availability


class BooksSpider(scrapy.Spider):
    name = "books"

    def start_requests(self) -> scrapy.Request:
        urls = ["https://books.toscrape.com/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        for book in response.css(".image_container"):
            yield scrapy.Request(
                url=response.urljoin(book.css("a::attr(href)").get()),
                callback=self.parse_book,
            )

        next_page = response.css(".next > a::attr(href)").get()

        if next_page is not None:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )

    @staticmethod
    def parse_book(response: Response) -> dict:
        title = response.css("h1::text").get()
        price = response.css(
            ".price_color::text"
        ).get().replace("£", "").strip()

        availability_text = response.css("p.instock.availability").get()
        amount_in_stock = get_availability(availability_text)

        rating = response.css(
            "p.star-rating::attr(class)"
        ).get().split(" ")[-1].lower()
        category = response.css("ul > li > a::text").getall()[-1]
        description = response.css(".sub-header + p::text").get()
        upc = response.css(
            ".table.table-striped tr th:contains('UPC') + td::text"
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
