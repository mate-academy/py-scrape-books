import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book(book: Response) -> dict:
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": book.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": int(
                "".join(
                    [
                        num
                        for num in book.css("tr:nth-child(6) > td::text").get()
                        if num.isdigit()
                    ]
                )
            ),
            "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
            "category": book.css("li:nth-child(3) a::text").get(),
            "description": book.css("article > p::text").get(),
            "upc": book.css(".table tr:nth-child(1) td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css(".product_pod").css("h3 a::attr(href)"):
            yield scrapy.Request(
                response.urljoin(book.get()), callback=self.parse_book
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)
