from typing import Generator
import scrapy
from scrapy.http import Response
from ..items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, res: Response, **kwargs) -> Generator:
        links_detail_pref = res.css("h3>a::attr(href)").getall()
        for prefix in links_detail_pref:
            yield res.follow(prefix, callback=self.parse_detail)

        next_pref = res.css("li.next>a::attr(href)").get()
        if next_pref:
            yield res.follow(next_pref, callback=self.parse)

    @staticmethod
    def parse_detail(res: Response) -> Generator:
        obj_rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        amount_in_stock = res.css("p.availability::text").re_first(r"\d+")
        rating_str = res.css("p.star-rating::attr(class)").get().split(" ")[-1]
        category = res.css("ul.breadcrumb > li:nth-child(3) a::text").get()
        item = BookItem()
        item["title"] = res.css("div.product_main>h1::text").get()
        item["price"] = res.css("p.price_color::text").get().replace("£", "")
        item["amount_in_stock"] = amount_in_stock
        item["rating"] = obj_rating[rating_str]
        item["category"] = category
        item["description"] = res.css("#product_description + p::text").get()
        item["upc"] = res.css(".table-striped tr:first-child > td::text").get()
        yield item
        # yield {
        #     "title": res.css("div.product_main>h1::text").get(),
        #     "price": res.css("p.price_color::text").get().replace("£", ""),
        #     "amount_in_stock": amount_in_stock,
        #     "rating": obj_rating[rating_str],
        #     "category": category,
        #     "description": res.css(".product_page > p::text").get(),
        #     "upc": res.css(".table-striped tr:first-child > td::text").get(),
        # }
