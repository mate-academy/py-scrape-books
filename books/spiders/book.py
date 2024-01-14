import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_page = book.css("h3 a::attr(href)").get()

            yield response.follow(url=book_page,
                                  callback=self.parse_books)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_books(response: Response):
        yield {
            "title":
                response.css("h1::text").get(),
            "price":
                response.css(".price_color::text").get(),
            "amount_in_stock":
                response.css(
                    "p.availability"
                ).get().split()[-3].replace("(", ""),
            "rating":
                len(response.css(".star-rating::text").getall()),
            "category":
                response.css(
                    ".breadcrumb > li:nth-last-child(2) > a::text"
                ).get(),
            "description":
                response.css("#product_description + p::text").get().strip(),
            "upc":
                len(response.css("td::text").get()),
        }
