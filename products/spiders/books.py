import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".col-sm-8"):
            detail_url = product.css("h3 a::attr(href)").get()
            if detail_url:
                yield response.follow(detail_url, self.parse_book_detail)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book_detail(self, response: Response):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("p.instock.availability::text").get().strip(),
            "rating": response.css("p.star-rating::attr(class)").get().replace("star-rating ", ""),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("div#product_description + p::text").get(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }
