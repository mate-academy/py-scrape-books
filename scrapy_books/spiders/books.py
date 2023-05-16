import re

import cssselect
import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        books_page = response.css(".product_pod")
        for book in books_page:
            book_url = self.get_detail_book_page_url(book)
            yield response.follow(
                book_url, callback=self.parse_detail_book_page
            )

        next_page_url = response.css("li.next a::attr(href)").get()

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    def get_detail_book_page_url(self, book: cssselect) -> str:
        relative_url = book.css("h3 a ::attr(href)").get()

        if "catalogue/" in relative_url:
            book_url = "https://books.toscrape.com/" + relative_url
        else:
            book_url = "https://books.toscrape.com/catalogue/" + relative_url

        return book_url

    def parse_detail_book_page(self, response: Response) -> None:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(
                ".product_main p::text").get().replace("£", ""),
            "amount_in_stock": re.findall(
                r"\d+", response.css("table tr")[5].css("td::text").get()
            )[0],
            "rating": response.css(
                "p.star-rating").attrib["class"].split()[-1],
            "category": response.xpath(
                "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
            ).get(),
            "description": response.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
            "upc": response.css("table tr")[0].css("td::text").get(),
        }
