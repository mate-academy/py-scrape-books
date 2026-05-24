import scrapy
from scrapy.http import Response


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def nbsp_remover(self, text: str):
        return text.replace(" ", "")

    def parse_book(self, book_body: Response):
        rating_dictionary = {
            "One": "1",
            "Two": "2",
            "Three": "3",
            "Four": "4",
            "Five": "5"
        }

        return {
            "title": book_body.css("h1::text").get(),
            "price": book_body.css("p.price_color::text").get()[1:],
            "amount_in_stock": book_body.css("p.instock::text").re(r"\d+")[0],
            "rating": rating_dictionary[
                book_body.css("p.star-rating::attr(class)").get().rsplit(maxsplit=1)[-1]
            ],
            "category": book_body.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            "description": self.nbsp_remover(
                book_body.css("#product_description + p::text").get()
            ),
            "upc": book_body.css("table tr:first-child td::text").get()
        }

    def parse(self, response: Response):
        for book_url in response.css("a[title]::attr(href)").getall():
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
