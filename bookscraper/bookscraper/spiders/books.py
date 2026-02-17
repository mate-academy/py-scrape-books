import scrapy
from bookscraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        book_links = response.css(
            "article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_page)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(self, response):
        book = BookItem()

        book["title"] = response.css("div.product_main h1::text").get()
        book["price"] = response.css("p.price_color::text").get()
        book["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()").get()
        book["category"] = response.xpath(
            "//ul[@class='breadcrumb']/li[3]/a/text()").get()
        book["description"] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()").get()

        availability_text = response.css(
            "p.instock.availability::text").getall()
        availability_text = "".join(availability_text).strip()
        book["amount_in_stock"] = self.extract_stock_count(availability_text)

        rating_class = response.css("p.star-rating::attr(class)").get()
        book["rating"] = self.convert_rating(rating_class)

        yield book

    def extract_stock_count(self, text):
        if text:
            import re
            match = re.search(r"\((\d+)\s+available\)", text)
            if match:
                return int(match.group(1))
        return 0

    def convert_rating(self, rating_class):
        ratings_map = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        if rating_class:
            classes = rating_class.split()
            for c in classes:
                if c in ratings_map:
                    return ratings_map[c]
        return 0
