import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".availability::text").re_first(
                r"\d+"
            ),
            "rating": response.css(".star-rating::attr(class)")
            .get()
            .split()[-1],
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(
                ".table-striped tr:nth-child(1) td::text"
            ).get(),
        }
