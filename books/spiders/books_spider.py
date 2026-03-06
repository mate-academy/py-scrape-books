import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):

        books = response.css(".product_pod")

        for book in books:
            href = book.css("h3 a::attr(href)").get()
            book_url = response.urljoin(href)

            yield scrapy.Request(
                url=book_url,
                callback=self.parse_book
            )

        next_page = response.css(".next a::attr(href)").get()

        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )

    def parse_book(self, response):

        rating_class = response.css(".star-rating::attr(class)").get()
        rating = rating_class.split()[-1]

        yield {
            "title": response.css(".product_main h1::text").get(),

            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),

            "amount_in_stock": response.css(
                ".instock.availability::text"
            ).re_first(r"\d+"),

            "rating": rating,

            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),

            "description": response.css(
                "#product_description + p::text"
            ).get(),

            "upc": response.css(
                "table tr:first-child td::text"
            ).get(),
        }
