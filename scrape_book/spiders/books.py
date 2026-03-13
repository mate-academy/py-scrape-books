import scrapy
from scrapy.http import Response
import re
from scrape_book.items import ScrapeBookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, callback=self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs):
        item = ScrapeBookItem()
        item["title"] = response.css("div.product_main h1::text").get()

        price_text = response.css("p.price_color::text").get()
        item["price"] = None
        if price_text:
            item["price"] = float(price_text.replace("£", ""))

        texts = response.css("p.instock.availability::text").getall()
        cleaned = " ".join(t.strip() for t in texts if t.strip())
        m = re.search(r"(\d+)\s+available", cleaned)
        item["amount_in_stock"] = int(m.group(1)) if m else None

        rating_class = response.css("p.star-rating::attr(class)").get()
        item["rating"] = rating_class.split()[-1] if rating_class else None

        crumbs = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = crumbs[-1].strip()

        item["description"] = response.css("#product_description ~ p::text").get(default="").strip() # ~ - next to

        item["upc"] = response.css("table.table.table-striped tr:nth-child(1) td::text").get()

        yield item
