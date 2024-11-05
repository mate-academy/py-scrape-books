import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            detail_page_url = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_page_url, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".instock.availability::text").re_first(r'\d+'),
            "rating": response.css("p.star-rating::attr(class)").re_first(r"star-rating (\w+)"),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("table.table-striped tr:nth-child(1) td::text").get(),
        }
