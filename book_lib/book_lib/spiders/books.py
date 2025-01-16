import scrapy
from scrapy.http import Response
from typing import Dict, Optional
from book_lib.items import BookLibItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def get_rating(self, book: scrapy.Selector) -> int:
        """Check book rating and return it as an integer."""
        rating_class = book.css(".star-rating::attr(class)").get()
        if rating_class:
            rating_class = rating_class.split()[-1]
            rating_map = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5,
            }
            return rating_map.get(rating_class, 0)
        return 0

    def parse(self, response: Response) -> scrapy.Request:
        """Parse the main page and extract book links."""
        books = response.css(".product_pod")
        for book in books:
            book_url = book.css("h3 a::attr(href)").get()
            book_page_url = response.urljoin(book_url)

            yield scrapy.Request(
                url=book_page_url,
                callback=self.parse_book_page
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_book_page(self, response: Response) -> Dict[str, Optional[str]]:
        """Parse the book page and extract the necessary information."""
        item = BookLibItem()  # Создаём экземпляр Item для книги

        item["title"] = response.css("h1::text").get()
        item["price"] = float(
            response.css(".price_color::text").get().replace("£", "")
        )
        item["upc"] = response.css("th:contains('UPC') + td::text").get()
        stock = response.css("th:contains('Availability') + td::text").get()
        item["description"] = response.css(
            "meta[name='description']::attr(content)"
        ).get()

        if stock:
            item["availability"] = int(stock.split(" ")[-2][1:])
        else:
            item["availability"] = 0

        # Дополнительно можно добавить рейтинг
        item["rating"] = self.get_rating(response)

        yield item
