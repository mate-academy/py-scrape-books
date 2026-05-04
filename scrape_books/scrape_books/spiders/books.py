import scrapy
from scrapy.http import Response

from scrape_books.scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self,response: Response, **kwargs):
        item = ScrapeBooksItem()

        item["title"] = response.css(".product_main h1::text").get()
        item["price"] = response.css(".price_color::text").get()
        item["amount_in_stock"] = response.css(".availability::text").re_first(r"\d+")
        item["rating"] = response.css(".star-rating::attr(class)").re_first(r"star-rating (\w+)")
        item["category"] = response.css(".breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css("#product_description ~ p::text").get(default="").strip()
        item["upc"] = response.css("th:contains('UPC') + td::text").get()

        yield item
