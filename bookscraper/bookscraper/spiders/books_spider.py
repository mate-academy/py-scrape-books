import scrapy
from scrapy.http import Response
from typing import Iterable, Any


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Iterable[scrapy.Request]:
        books = response.css("article.product_pod h3 a::attr(href)").getall()

        for book_url in books:
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Iterable[dict[str, Any]]:
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_class = response.css("p.star-rating::attr(class)").get()

        rating = None
        if rating_class:
            rating_word = rating_class.split(" ")[-1]
            rating = rating_map.get(rating_word)

        stock_text = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")

        amount_in_stock = int(stock_text) if stock_text else 0

        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": response.xpath(
                '//ul[@class="breadcrumb"]/li[3]/a/text()'
            ).get(),
            "description": response.xpath(
                '//div[@id="product_description"]/following-sibling::p/text()'
            ).get(),
            "upc": response.xpath(
                '//th[text()="UPC"]/following-sibling::td/text()'
            ).get(),
        }
