import scrapy
from scrapy.http import Response
from typing import Generator

class BooksSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"
                  "/catalogue/category/books_1/index.html"]

    def parse(self, response: Response, **kwargs) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            url = book.css("h3 > a::attr(href)").get()

            if url is not None:
                book_url = response.urljoin(url)
                yield scrapy.Request(book_url, callback=self.parce_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def parce_book(response: Response) -> dict:
        book_exp = {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get()[1::],
            "amount_in_stock":
                response.css("p.availability::text").re_first(r"\d+"),
            "rating": response
                .css(".star-rating::attr(class)").get().split(" ")[-1],
            "category": response
                .css(".breadcrumb > li > a::text").getall()[-1],
            "description": response.css("article > p::text").get(),
            "UPC": response.css("tr > td::text").getall()[0],
        }
        return book_exp
