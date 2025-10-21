import scrapy
from scrapy.http import Response

from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/"
    ]

    RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        # перейти на наступну сторінку, якщо є
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        price = 0.0
        amount_in_stock = 0
        raw_price = response.css("p.price_color::text").get()
        if raw_price is not None:
            price = float(raw_price.replace("£", "").strip())
        rating = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (\w+)"
        )
        raw_amount = (
            response.css("p.instock.availability::text").re_first(r"\d+")
        )
        if raw_amount is not None:
            amount_in_stock = int(raw_amount)

        item = ScrapeBooksItem()

        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = price
        item["amount_in_stock"] = amount_in_stock
        item["rating"] = self.RATING_MAP.get(rating, 0)
        item["category"] = (
            response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        )
        item["description"] = (
            response.css("#product_description ~ p::text").get()
        )
        item["upc"] = response.css(
            "table.table.table-striped tr:nth-child(1) td::text"
        ).get()

        yield item
