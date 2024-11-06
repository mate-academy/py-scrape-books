import scrapy
from scrapy.shell import inspect_response

from app.items import BookItem


rating_number = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]

    def __init__(self, last_page: int = 1, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_page = int(last_page)

    def start_requests(self):
        base_url = "https://books.toscrape.com/catalogue/page-{}.html"

        for i in range(1, self.last_page + 1):
            url = base_url.format(i)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            self.log("Found url: {}".format(href))
            yield response.follow(href, self.parse_book_details)

    def parse_book_details(self, response):
        item = BookItem()

        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["amount_in_stock"] = response.css("p.instock.availability::text").re_first(
            r"In stock \((\d+) available\)"
        )
        item["rating"] = rating_number.get(
            response.css("p.star-rating::attr(class)").get().split()[1].lower()
        )
        item["category"] = response.css("ul.breadcrumb li:nth-of-type(3) a::text").get()
        item["description"] = response.xpath('//*[@id="content_inner"]/article/p/text()').get()
        item["upc"] = response.css("table.table tr:nth-of-type(1) td::text").get()

        return item
