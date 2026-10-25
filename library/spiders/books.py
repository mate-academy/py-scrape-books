from collections.abc import Iterator

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]
    book_count = 0
    book_limit = 1000

    def parse(self, response: Response, **kwargs) -> Iterator[scrapy.Request]:
        if self.book_count >= self.book_limit:
            raise CloseSpider("limit_reached")

        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self._parse_book_info)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_info(
            self,
            response: Response
    ) -> Iterator[dict[str, str | int | float | None]]:
        if self.book_count >= self.book_limit:
            raise CloseSpider("limit_reached")

        title = response.css(".product_main h1::text").get()
        price = response.css(".product_main .price_color::text").get()
        stock = response.css(".product_main .availability::text").getall()
        rating = response.css(
            ".product_main .star-rating::attr(class)"
        ).get()
        category = response.css(".breadcrumb > li")
        description = response.css("#product_description + p::text").get()
        upc = response.css(
            '.table-striped tr:contains("UPC") td::text'
        ).get()

        stock_words = stock[-1].split() if stock else []
        rating_words = rating.split() if rating is not None else []

        item = {
            "title": title,
            "price": float(
                price.replace("£", "")
            ) if price is not None else None,
            "amount_in_stock": (
                int(stock_words[-2].replace("(", ""))
                if len(stock_words) >= 2 else None
            ),
            "rating": rating_words[1] if len(rating_words) >= 2 else None,
            "category": (
                category[-2].css("a::text").get()
                if len(category) >= 2 else None
            ),
            "description": description,
            "upc": upc
        }
        self.book_count += 1
        yield item

        if self.book_count >= self.book_limit:
            raise CloseSpider("limit_reached")
