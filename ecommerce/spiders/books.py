import scrapy
from ecommerce.items import EcommerceItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response):
        for book_link in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        price_text = response.css(".price_color::text").get()
        price = float(price_text.replace("£", "")) if price_text else 0.0

        rating_class = response.css(".star-rating::attr(class)").get()
        rating_word = rating_class.split()[-1] if rating_class else ""

        upc = response.css("table tr:nth-child(1) td::text").get()

        stock_text = response.css("table tr:nth-child(6) td::text").get() or ""
        stock_numbers_only = "".join(char for char in stock_text if char.isdigit())
        amount_in_stock = int(stock_numbers_only) if stock_numbers_only else 0

        yield EcommerceItem(
            title=response.css("h1::text").get(),
            price=price,
            amount_in_stock=amount_in_stock,
            rating=self.RATING_MAP.get(rating_word, 0),
            category=response.css(".breadcrumb li:nth-last-child(2) a::text").get(),
            description=response.css("#product_description + p::text").get(),
            upc=upc,
        )
