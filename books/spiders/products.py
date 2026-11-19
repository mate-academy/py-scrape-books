import scrapy
from scrapy.http import Response

from books.items import BooksItem

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        yield from response.follow_all(response.css(".product_pod h3 a"), callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> BooksItem:
        yield BooksItem(
            title=response.css("h1::text").get(),
            price=float(response.css("p.price_color::text").get().replace("£", "")),
            amount_in_stock=int(response.css("p.availability::text").re_first(r"(\d+) available")),
            rating=RATINGS[response.css("p.star-rating::attr(class)").get().split()[-1]],
            category=response.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.css("table.table-striped tr:first-child td::text").get(),
        )
