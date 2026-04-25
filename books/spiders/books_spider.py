import scrapy
from typing import Generator
from word2number import w2n
import re
from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: scrapy.http.Response
              ) -> Generator[scrapy.Request, None, None]:
        for book in response.css("article.product_pod"):
            partial_data = {
                "title": book.css("h3 a::attr(title)").get(),
                "price": float(book.css(
                    "p.price_color::text").get(
                    default="0.0").replace("£", "")),
                "rating": w2n.word_to_num(book.css(
                    "p.star-rating::attr(class)").get(
                    default="Zero").split()[-1])
            }

            book_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                book_url,
                callback=self.parse_one_book,
                cb_kwargs={"partial_data": partial_data}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_one_book(
            self, response: scrapy.http.Response, partial_data: dict
    ) -> Generator[BooksItem, None, None]:
        def extract_with_css(query: str) -> str:
            return response.css(query).get(default="").strip()

        stock_text = extract_with_css("table.table tr:nth-child(6) td::text")
        stock_match = re.search(r"\d+", stock_text)

        yield BooksItem({
            **partial_data,
            "amount_in_stock": int(stock_match.group()) if stock_match else 0,
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": extract_with_css("#product_description ~ p::text"),
            "upc": extract_with_css("table.table tr:nth-child(1) td::text"),
        })
