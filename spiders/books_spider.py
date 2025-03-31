import re

import scrapy

from py_scrape_books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: scrapy.http.Response) -> scrapy.Request:
        books = response.css("article.product_pod")
        for book in books:
            detail_url = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: scrapy.http.Response) -> scrapy.Request:
        item = BookItem()
        item["title"] = response.css("div.product_main h1::text").get()

        item["price"] = response.css("p.price_color::text").get()

        stock_text = response.css("p.instock.availability::text").getall()
        stock_text = "".join(stock_text).strip()
        match = re.search(r"\((\d+)\s+available\)", stock_text)
        item["amount_in_stock"] = match.group(1) if match else None

        rating_class = response.css("p.star-rating").attrib.get("class", "")
        rating = rating_class.replace("star-rating", "").strip()
        item["rating"] = rating

        breadcrumbs = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = breadcrumbs[2].strip() \
            if len(breadcrumbs) >= 3 else ""

        description = response.xpath(
            '//div[@id= "product_description"]/following-sibling::p/text()'
        ).get()
        item["description"] = description

        item["upc"] = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        yield item