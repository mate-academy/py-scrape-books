import scrapy
from scrapy.http import Response
import re


class ExampleSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs):
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        cls = response.css("p.star-rating::attr(class)").get() or ""
        raw_stock = response.xpath("//th[normalize-space()='Availability']/following-sibling::td/text()").get()
        amount_in_stock = int(re.search(r"\d+", raw_stock).group()) if raw_stock else 0

        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get().strip().replace("£", "")),
            "amount_in_stock": amount_in_stock,
            "rating": rating.get(cls.split()[-1], 0),
            "category": response.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.xpath("//th[normalize-space()='UPC']/following-sibling::td/text()").get(),
        }
