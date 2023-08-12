import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        # "h3 a::attr(href)" == "h3 > a::attr(href)"
        # book_urls = response.css(".product_pod > a::attr(href)").getall()
        book_urls = response.css("h3 a::attr(href)").getall()

        for book_url in book_urls:
            yield response.follow(book_url, callback=self.parse_single_book)

        # next_page = response.css(".pager > li.next > a::attr(href)").get()
        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_single_book(response: Response) -> None:
        yield {
                "title": response.css(".product_main > h1::text").get()
            }
