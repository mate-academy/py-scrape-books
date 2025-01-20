import scrapy
from scrapy.http import Response
from books.items import BooksItem


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            detail_link = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        book = BooksItem()

        book["title"] = response.css(".product_main h1::text").get()
        book["price"] = response.css(".price_color::text").get()
        book["amount_in_stock"] = response.css(".availability::text").getall()[1].strip()
        book["rating"] = response.css(".star-rating::attr(class)").get().split()[-1]
        book["category"] = response.css(".breadcrumb li:nth-child(3) a::text").get()
        book["description"] = response.css("#product_description + p::text").get()
        book["upc"] = response.css(".table tr:nth-child(1) td::text").get()

        yield book
