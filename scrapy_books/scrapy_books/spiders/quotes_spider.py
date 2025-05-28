from pathlib import Path

import scrapy
from scrapy.http import Response
from scrapy_books.items import ScrapyBooksItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        product_links = response.css(".product_pod h3 a::attr(href)").getall()

        for link in product_links:
            yield response.follow(link, callback=self.parse_product_details)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product_details(self, response: Response, **kwargs):
        rating_text = response.css(
            ".star-rating::attr(class)"
        ).re_first(r"star-rating (\w+)")
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        item = ScrapyBooksItem()

        item["title"] = response.css(".product_main h1::text").get()
        item["price"] = response.css(".price_color::text").get()
        item["amount_in_stock"] = response.css(
            ".instock.availability::text"
        ).re_first(r"\d+") or "0"
        
        item["rating"] = rating_map.get(rating_text, 0)
        
        item["category"] = response.css(
            ".breadcrumb li:nth-child(3) a::text"
        ).get() or "Unknown Category"
        item["description"] = response.css(
            "#product_description + p::text"
        ).get() or "No Description Available"
        item["upc"] = response.xpath(
            "//table[@class='table table-striped']\
                //tr[th[text()='UPC']]/td/text()"
        ).get() or "Unknown UPC"

        yield item
