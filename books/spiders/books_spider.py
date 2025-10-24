import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    
    custom_settings = {
        "FEEDS": {
            "books.jl": {"format": "jsonlines"},
        }
    }

    start_urls = [
        "https://books.toscrape.com/catalogue/page-1.html",
    ]

    def parse_one_book(self, response: Response):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(response.css(".price_color::text").get(default="0").lstrip("£")),
            "amount_in_stock": response.css(".instock::text").re_first("\d+"),
            "rating": w2n.word_to_num(response.css(".star-rating").re_first("star-rating ([A-Za-z]+)")),
            "category": response.css(".breadcrumb li a::text").getall()[-1],
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css(".table td::text").get(),
        }

    def parse(self, response: Response):
        books_urls = response.css("article.product_pod h3 a::attr(href)").getall()
        yield from response.follow_all(books_urls, callback=self.parse_one_book)

        next_url = response.css(".next a::attr(href)").get()
        if next_url:
            yield response.follow(next_url, callback=self.parse)
