import scrapy
from scrapy.http import Response


STARS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksToscrapeSpider(scrapy.Spider):
    name = "books_toscrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("h3 > a::attr(href)").getall():
            yield response.follow(book, callback=self._parse_single_book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_single_book(response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css("p.price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css("p.instock::text")
                .getall()[1]
                .split()[2]
                .replace("(", "")
            ),
            "rating": STARS.get(
                response.css(".product_main .star-rating")
                .xpath("@class")
                .extract()[0]
                .split()[-1]
            ),
            "category": response.css(".breadcrumb li > a::text").getall()[-1],
            "description": response.css(
                "article.product_page > p::text"
            ).get(),
            "upc": response.css("table td::text").get(),
        }
