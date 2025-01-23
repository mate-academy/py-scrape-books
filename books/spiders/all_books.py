import sys

import scrapy
import logging
from scrapy.http import Response
from word2number import w2n

from books.items import BookItem



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("all_books.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


class AllBooksSpider(scrapy.Spider):
    name = "all_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    book_counter = 1

    def parse_book(self, response: Response, book_number: int) -> BookItem:
        try:
            book = BookItem(
                title=response.css("h1::text").get(),
                price=float(
                    response.css(".price_color::text").re_first(r"[\d.]+")
                ),
                amount_in_stock=int(
                    "".join(response.css(
                        "div.product_main .instock::text"
                    ).re_first(r"\d+"))
                ),
                rating=w2n.word_to_num(
                    response.css(
                        "div.product_main p[class~=star-rating]::attr(class)"
                    ).get().split()[-1]
                ),
                category=response.css("ul.breadcrumb a::text").getall()[-1],
                description=response.css(
                    "#content_inner > article > p::text"
                ).get(),
                upc=response.css("tr:nth-child(1) td::text").get()
            )
            logging.info(f"Book {book_number} has been parsed.")
            return book
        except ValueError as error:
            logging.error(f"ValueError has occurred: {error}")
        except AttributeError as error:
            logging.error(f"ValueError has occurred: {error}")
        except IndexError as error:
            logging.error(f"IndexError has occurred: {error}")

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_number = self.book_counter
            logging.info(f"Start parsing book  No {book_number}/1000.")
            detail_page_url = book.css("h3 a::attr(href)").get()

            self.book_counter += 1

            yield response.follow(detail_page_url, callback=self.parse_book, cb_kwargs={"book_number": book_number})

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
