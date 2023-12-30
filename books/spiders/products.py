import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css(".image_container > a::attr(href)").get()
            yield response.follow(url=book_url, callback=self.parse_book_detail)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    @staticmethod
    def parse_book_detail(book: Response):

        yield {
            "title": book.css(".product_main > h1::text").get()   ,
            "price": book.css(".price_color::text").get(),
            "amount_in_stock": (
                book.css(".instock").get().split()[-3].replace("(", "")
            ),
            "rating": book.css(".star-rating::attr(class)").get().split()[-1],
            "category": (
                book.css(".breadcrumb > li:nth-last-child(2) > a::text").get()
            ),
            "description": book.css(".product_page > p::text").get(),
            "upc": book.css("th:contains('UPC') + td::text").get()
        }
