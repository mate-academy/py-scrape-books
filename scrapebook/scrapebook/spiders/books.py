import scrapy
from scrapy.http import Response


RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        detail_urls = response.css("article > h3 > a::attr(href)").getall()
        for detail_url in detail_urls:
            yield response.follow(detail_url, callback=self.parse_single_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_single_book(response: Response) -> dict:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(
                "p.price_color::text"
            ).get().replace("£", ""),
            "amount_in_stock": int(response.css(
                ".table-striped tr td::text"
            ).getall()[-2].split()[-2].replace("(", "")),
            "rating": RATINGS[
                response.css(
                    ".star-rating::attr(class)"
                ).get().split()[-1]
            ],
            "category": response.css(
                "ul > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css(
                ".table-striped tr td::text"
            ).getall()[0]
        }
