from urllib.parse import urljoin
import scrapy
import re

from scrapy.http import Response, Request
from typing import Generator

from bookscraper.bookscraper.items import BookscraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    def parse(
            self,
            response: Response
    ) -> Generator[Request, None, None]:
        category_urls = response.css(
            "div.side_categories ul li ul li a::attr(href)"
        ).getall()
        for url in category_urls:
            absolute_url = urljoin(response.url, url)
            yield scrapy.Request(absolute_url, callback=self.parse_category)

    def parse_category(
            self,
            response: Response
    ) -> Generator[Request, None, None]:
        book_urls = response.css("h3 a::attr(href)").getall()
        for url in book_urls:
            absolute_url = urljoin(response.url, url)
            yield scrapy.Request(absolute_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            absolute_url = urljoin(response.url, next_page)
            yield scrapy.Request(absolute_url, callback=self.parse_category)

    def parse_book(
            self,
            response: Response
    ) -> Generator[BookscraperItem, None, None]:
        table_rows = response.css("table tr")
        availability_text = response.css(
            "p.instock.availability::text"
        ).getall()
        availability_cleaned = "".join(availability_text).strip()

        match = re.search(r"\((\d+) available\)", availability_cleaned)
        amount_in_stock = int(match.group(1)) if match else 0

        book_item = BookscraperItem()
        book_item["title"] = response.css("h1::text").get()
        book_item["price"] = response.css("p.price_color::text").get()
        book_item["amount_in_stock"] = amount_in_stock
        book_item["rating"] = (
            response.css("p.star-rating::attr(class)").get().split()[-1]
        )
        book_item["category"] = response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get()
        book_item["description"] = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).get()
        book_item["upc"] = table_rows[0].css("td::text").get()

        yield book_item
