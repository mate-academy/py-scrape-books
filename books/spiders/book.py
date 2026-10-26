from pathlib import Path

import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    book_count = 0

    def parse(self, response):
        for book in response.css(".product_pod"):
            if self.book_count >= 1000:
                return
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        if self.book_count < 1000:
            next_page = response.css(".next a::attr(href)").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        if self.book_count >= 1000:
            return

        self.book_count += 1
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": (
                response.xpath(
                    '//th[text()="Availability"]/following-sibling::td/text()'
                ).get()
                or ""
            ).strip(),
            "rating": (response.css(".star-rating::attr(class)").get() or "")
            .replace("star-rating", "")
            .strip(),
            "category": response.xpath(
                '//ul[@class="breadcrumb"]/li[3]/a/text()'
            ).get(),
            "description": response.xpath(
                '//div[@id="product_description"]/following-sibling::p[1]/text()'
            ).get(),
            "upc": (
                response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
                or ""
            ).strip(),
        }
