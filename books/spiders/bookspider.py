import scrapy
from scrapy.http import Response


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

    def parse(self, response: Response) -> dict:
        for book in response.css("article.product_pod"):
            detail_page_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(detail_page_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css("p.price_color::text").get().strip("£")
            ),
            "amount_in_stock": int(
                response.css(
                    "p.instock.availability"
                ).get().split()[-3].strip("(")
            ),
            "rating": self.rating.get(
                response.css(
                    "p.star-rating::attr(class)"
                ).get().split()[-1]),
            "category": response.css("li a::text").getall()[2],
            "description": response.css("div.sub-header + p::text").get(),
            "upc": response.css("td::text").getall()[0]
        }
