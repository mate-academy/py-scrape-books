import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def get_single_book(self, response: Response):
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get()[1:],
            "amount_in_stock": response.css(".instock.availability::text").re_first(
                r"\d+"
            ),
            "rating": w2n.word_to_num(
                response.css(".star-rating::attr(class)").get().split(" ")[-1]
            ),
            "category": response.css("a[href*='category']::text").getall()[-1],
            "description": response.css("#product_description+p::text").get(),
            "upc": response.css("td::text").get(),
        }

    def parse(self, response, **kwargs):
        for book in response.css(".product_pod"):
            detailed_book_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(detailed_book_url, callback=self.get_single_book)

        for a in response.css(".next a"):
            yield response.follow(a, callback=self.parse)
