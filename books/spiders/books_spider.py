import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/catalogue/category/books_1/page-1.html"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(url=response.urljoin(book_url), callback=self.parse_book_detail)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_book_detail(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").re_first(r"£([\d\.]+)")),
            "amount_in_stock": int(response.css(".instock.availability::text").re_first(r"\((\d+) available\)")),
            "rating": self.parse_rating(response.css("p.star-rating::attr(class)").get()),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("meta[name='description']::attr(content)").get(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }

    def parse_rating(self, rating_class):
        ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return ratings.get(rating_class.split(" ")[-1])
