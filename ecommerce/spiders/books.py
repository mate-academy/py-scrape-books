import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book_url in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(book_url, callback=self.parse_book)

        next_page_url = response.css("li.next a::attr(href)").get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> dict:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": int(response.css(".instock.availability::text").re_first(r"\d+")),
            "rating": response.css("p.star-rating::attr(class)").get().split()[-1],
            "category": response.css("li:nth-child(3) a::text").get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css(".table tr td::text").get()
        }
