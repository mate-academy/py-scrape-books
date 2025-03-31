import re

import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, last_page=1, **kwargs):
        super().__init__(**kwargs)
        self.last_page = int(last_page)

    def start_requests(self):
        base_url = "https://books.toscrape.com/catalogue/page-{}.html"
        headers = {"User-Agent": "Mozilla/5.0"}

        for i in range(1, self.last_page + 1):
            url = base_url.format(i)
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response: Response, **kwargs):
        for href in response.css("h3 a::attr(href)").getall():
            self.log("url: " + href)
            yield response.follow(href, callback=self.parse_book_detail)
        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_book_detail(self, response: Response):
        item = BooksItem()
        item["title"] = response.css("div.product_main h1::text").get()
        price_text = response.css("p.price_color::text").get()
        item["price"] = float(re.sub(r"[^\d.]", "", price_text))
        availability_list = response.css("p.instock.availability::text").getall()
        availability_text = " ".join(t.strip() for t in availability_list if t.strip())
        match = re.search(r"\((\d+)\s+available\)", availability_text)
        if match:
            item["amount_in_stock"] = int(match.group(1))
        else:
            item["amount_in_stock"] = 0

        item["rating"] = self.get_book_rating(response)
        item["description"] = response.css("#product_description + p::text").get(default="No description provided.")
        item["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        item["upc"] = response.css("table.table tr:nth-child(1) td::text").get()
        self.log(f"book title: {item['title']}")
        yield item

    def get_book_rating(self, response: Response):
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        return rating_map.get(rating_class.split()[-1], 0) if rating_class else 0