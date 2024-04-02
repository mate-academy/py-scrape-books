import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, self.parse_book)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, book: Response):
        yield {
            "title": book.css("div.product_main > h1::text").get(),
            "price": float(book.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                book.css("p.availability").get().split()[-3].replace("(", "")
            ),
            "rating": book.css(".star-rating::attr(class)").get().split()[-1],
            "category": book.css(".breadcrumb a::text").getall()[-1],
            "description": book.css(".product_page > p::text").get(),
            "upc": book.css("th:contains('UPC') + td::text").get(),
        }
