import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response):
        for book_link in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_link, callback=self.parse_book_detail)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response: Response):
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        rating_word = response.css("p.star-rating::attr(class)").get().split()[1]
        rating = rating_map.get(rating_word, 0)
        yield {
            "title": response.css(".col-sm-6.product_main h1::text").get(),
            "price": float(
                response.css("p.price_color *::text").re_first(r"[\d\.]+")
            ),
            "amount_in_stock": int(
                response.css("p.instock.availability::text").re_first(r"\d+")
            ),
            "rating": rating,
            "category": response.css(".breadcrumb li a::text").getall()[2],
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css("table tr td::text").get()
        }
