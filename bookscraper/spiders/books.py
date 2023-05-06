import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            yield response.follow(
                book.css("a[title]::attr(href)").get(),
                callback=self.parse_single_book
            )

        next_page = response.css(".pager > .next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response, **kwargs) -> dict:
        table = response.css(".table > tr > td::text").getall()
        yield dict(
            title=response.css(".product_main > h1::text").get(),
            price=table[2],
            amount_in_stock=table[5].replace("(", "").split()[2],
            rating=(
                response.css(".star-rating").xpath("./@class")
                .extract()[0].split()[-1]
            ),
            category=response.css(".breadcrumb > li > a::text").getall()[2],
            description=response.css(".product_page > p::text").get(),
            upc=table[0]
        )
