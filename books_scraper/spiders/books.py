import re

import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod h3 a")

        for book in books:
            href = book.attrib["href"]
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get()
        price = response.css("p.price_color::text").get()
        rating = response.css("p.star-rating::attr(class)").get().split()[-1]

        stock_text = response.css("p.instock.availability::text").getall()
        stock_text = [text.strip() for text in stock_text if text.strip()][0]
        amount_in_stock = int(re.search(r"\d+", stock_text).group())

        category = response.css("ul.breadcrumb li a::text").getall()[2]

        description = response.css("#product_description + p::text").get()

        upc = response.css("table tr:first-child td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
