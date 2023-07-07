from scrapy.http import Response


import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books_urls = response.css("h3 > a::attr(href)").getall()
        for book in books_urls:
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response):
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(response.css(
                ".availability::text"
            ).re_first(r"(\d+) available")),
            "rating": response.css(
                ".star-rating::attr(class)"
            ).get().split()[-1],
            "category": response.css(
                ".breadcrumb > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table > tr > td::text").get(),
        }
