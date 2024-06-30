from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class BooksScSpider(scrapy.Spider):
    name = "books_sc"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        books_links = self.get_books_links(response)
        for book_link in books_links:
            yield scrapy.Request(url=book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs) -> dict:
        return dict(
            title=response.css(".product_main h1::text").get(),
            price=float(response.css(".price_color::text").get()[1:]),
            amount_in_stock=self.parse_stock_availability(response),
            rating=self.parse_star_rating(response),
            category=response.css(".breadcrumb li a::text").getall()[-1],
            description=response.css("#product_description ~ p::text").get(),
            upc=response.css(
                'table.table.table-striped tr:contains("UPC") td::text'
            ).get(),
        )

    def parse_stock_availability(self, response: Response, **kwargs) -> int:
        availability_text = response.css(
            "p.instock.availability::text"
        ).getall()
        availability_text = (
            " ".join(availability_text).strip().replace("(", "")
        )
        stock_number = int(
            [word for word in availability_text.split() if word.isdigit()][0]
        )

        return stock_number

    def parse_star_rating(self, response: Response, **kwargs) -> int:
        star_rating_class = response.css("p.star-rating::attr(class)").get()
        rating_str = star_rating_class.split()[-1]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return rating_map.get(rating_str, 0)

    def get_books_links(self, response: Response, **kwargs) -> list[str]:
        books = response.css("li.col-xs-6.col-sm-4.col-md-3.col-lg-3")
        books_links = []
        for book in books:
            relative_link = book.css("div.image_container a::attr(href)").get()
            book_link = urljoin(response.url, relative_link)
            books_links.append(book_link)
        return books_links
