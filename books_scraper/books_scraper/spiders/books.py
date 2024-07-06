import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book_url in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_url, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response):
        yield {
            "title": self.parse_title(response),
            "price": self.parse_price(response),
            "amount_in_stock": self.parse_amount_in_stock(response),
            "rating": self.parse_rating(response),
            "category": self.parse_category(response),
            "description": self.parse_description(response),
            "upc": self.parse_upc(response),
        }

    def parse_title(self, response: Response):
        return response.css("h1::text").get()

    def parse_price(self, response: Response):
        return response.css("p.price_color::text").get()

    def parse_amount_in_stock(self, response: Response):
        return response.css("p.instock.availability::text").re_first("\d+")

    def parse_rating(self, response: Response):
        return response.css("p.star-rating::attr(class)").re_first("star-rating (\w+)")

    def parse_category(self, response: Response):
        return response.css("ul.breadcrumb li a::text")[-2].get()

    def parse_description(self, response: Response):
        return response.css('meta[name="description"]::attr(content)').get().strip()

    def parse_upc(self, response: Response):
        return response.css("table.table-striped tr:nth-child(1) td::text").get()
