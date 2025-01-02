import scrapy
from scrapy.http import Response
from typing import Generator


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def yield_next_page(self, response: Response) -> Generator[dict, None, None]:
        next_page = response.css(".next > a").css("a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_one_book(self, response: Response) -> Generator[dict, None, None]:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get().lstrip("£")),
            "amount_in_stock": response.css("p.availability").get().split()[-3].lstrip("("),
            "rating": response.css(".star-rating::attr(class)").get(),
            "category": response.css(".breadcrumb > li > a::text").getall()[2],
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("table > tr> td::text").getall()[0],
        }

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]:
        books = response.css(".product_pod")
        for book in books:
            detail_page = book.css("h3 > a::attr(href)").get()
            detail_page_url = response.urljoin(detail_page)
            yield scrapy.Request(url=detail_page_url, callback=self.parse_one_book)

        yield from self.yield_next_page(response)
