
from urllib.parse import urljoin
import scrapy
from scrapy.http import Response
from books_scrape.items import BooksScrapeItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }

    def parse(self, response: Response, **kwargs):

        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            absolute_url_book = urljoin(response.url, book_url)

            rating_text = book.css(".star-rating::attr(class)").get().split(" ")[-1]

            yield scrapy.Request(
                absolute_url_book,
                callback=self.parse_book,
                meta={
                    "title": book.css("h3 a::attr(title)").get(),
                    "price": book.css(".price_color::text").get().replace("£", ""),
                    "rating": self.RATING_MAP.get(rating_text, 0)
                }
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book(self, response: Response):
        availability_text = response.css(".availability::text").getall()[1].strip()
        available_quantity = int(availability_text.split('(')[1].split()[0])

        yield {
            'title': response.meta['title'],
            'price': response.meta['price'],
            'rating': response.meta['rating'],
            "category": response.css(".breadcrumb li:nth-last-child(2) a::text").get(),
            'description': response.css("#product_description + p::text").get(),
            'upc': response.css("th:contains('UPC') + td::text").get(),
            'available_quantity': available_quantity,
        }
