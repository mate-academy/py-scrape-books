import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, book: Response):
        yield {
            "title": book.css("div.col-sm-6 > h1::text").get(),
            "price": float(book.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                book.css("p.availability").get().split()[-3].replace("(", "")
            ),
            "rating": len(book.css(".star-rating").getall()),
            "category": book.css(".breadcrumb a::text").getall()[-1],
            "description": book.xpath("//p[not(@class)]").get(),
            "upc": book.css(".table-striped > td::text").get(),
        }
