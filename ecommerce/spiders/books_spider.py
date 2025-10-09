import re
import scrapy
from ecommerce.items import EcommerceItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0
        self.scheduled_count = 0
        self.limit = 1000

    def parse(self, response):
        for book in response.css("article.product_pod"):
            if self.scheduled_count >= self.limit:
                return

            book_url = book.css("h3 a::attr(href)").get()
            if book_url:
                self.scheduled_count += 1
                yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page and self.scheduled_count < self.limit:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        self.count += 1

        item = EcommerceItem()

        price_text = response.css("p.price_color::text").get()
        price = float(price_text.replace("£", "")) if price_text else None

        stock_text = "".join(response.css("p.instock.availability::text").getall()).strip()
        m = re.search(r"(\d+)", stock_text)
        amount_in_stock = int(m.group(1)) if m else None

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_word = rating_class.split()[-1] if rating_class else None
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = rating_map.get(rating_word)

        desc = response.css("#product_description ~ p::text").get()
        description = desc.strip() if desc else ""

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()

        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = price
        item["amount_in_stock"] = amount_in_stock
        item["rating"] = rating
        item["category"] = category
        item["description"] = description
        item["upc"] = upc

        yield item
