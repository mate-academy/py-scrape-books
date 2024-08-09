import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".col-xs-6.col-sm-4.col-md-3.col-lg-3"):
            relative_url = book.css("h3 a::attr(href)").get()
            book_url = response.urljoin(relative_url)

            yield scrapy.Request(book_url, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response: Response):
        rating_text = response.css("p.star-rating::attr(class)").re_first(r"\b(\w+)$")
        rating_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}.get(rating_text)

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": int(response.css("p.instock.availability::text").re_first(r"\d+")),
            "rating": rating_number,
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description ~ p::text").get(),
            "upc": response.css("table.table-striped tr:nth-child(1) td::text").get(),
        }
