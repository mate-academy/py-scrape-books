import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book(book: Response):
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": book.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": book.css(".availability::text").re_first(r'\d+'),
            "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
            "category": book.css("li:nth-child(3) a::text").get(),
            "description": book.css("article > p::text").get(),
            "upc": book.css("tr:nth-child(1) td::text").get(),
        }

    def parse(self, response: Response, **kwargs):
        book_links = response.css(".col-lg-3 a::attr(href)").getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css(".pager > .next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
