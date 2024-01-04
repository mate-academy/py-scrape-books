import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css(".product_pod"):
            book_link = book.css("h3 a::attr(href)").get()
            book_link = response.urljoin(book_link)
            yield scrapy.Request(url=book_link, callback=self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".instock").get().split()[7][1:],
            "rating": response.css(".star-rating::attr(class)").get(),
            "category": response.css(".breadcrumb li a::text").getall(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table tr td::text").get(),
        }
