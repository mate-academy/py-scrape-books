import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".image_container a::attr(href)"):
            yield response.follow(book, callback=self._parse_single_book)

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_single_book(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css(".instock::text").re_first(r"\d+")),
            "rating": response.css(".star-rating::attr(class)").get().split()[-1],
            "category": response.css(".breadcrumb a::text").getall()[-1],
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("table td::text").getall()[0]
        }
