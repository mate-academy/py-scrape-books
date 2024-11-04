import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail_page = book.css("h3 > a::attr(href)").get()
            yield response.follow(
                detail_page,
                callback=self._parse_detail_book
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detail_book(self, response: Response):
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".instock::text").re_first(r"\d+")
            ),
            "rating": (
                response.css(".star-rating::attr(class)").get().split()[1]
            ),
            "category": (
                response.css(".breadcrumb > li")[2].css("a::text").get()
            ),
            "description": response.css("article > p::text").get(),
            "upc": (
                response.css(
                    ".table.table-striped tr:nth-child(1) td::text"
                )
                .get()
            )
        }
