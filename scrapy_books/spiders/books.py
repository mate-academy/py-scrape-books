import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books_page = response.css(".product_pod")

        for book in books_page:
            relative_url = book.css('h3 a ::attr(href)').get()
            book_url = "https://books.toscrape.com/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page_url = response.css('li.next a::attr(href)').get()

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response: Response):

        yield {
            "title": response.css('.product_main h1::text').get(),
            "price": response.css('.product_main p::text').get().replace("£", ""),
            "amount_in_stock": re.findall(r'\d+', response.css("table tr")[5].css('td::text').get())[0],
            "rating": response.css("p.star-rating").attrib['class'],
            "category": response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            "upc": response.css("table tr")[0].css('td::text').get(),
        }

