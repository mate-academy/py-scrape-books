import scrapy
from scrapy.http import Response


RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def get_digits_from_string(arg: str):
    return int("".join([x for x in arg if x.isdigit()]))


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book(book: Response):
        yield {
            "title": book.css("h1::text").get(),
            "price": float(book.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": get_digits_from_string(
                book.css("tr:nth-child(6) td::text").get()
            ),
            "rating": RATINGS[book.css("p.star-rating::attr(class)").get().split()[1]],
            "category": book.css("#default > div > div > ul > li:nth-child(3) > a::text").get(),
            "description": book.css("#content_inner > article > p::text").get(),
            "upc": book.css("tr:nth-child(1) td::text").get()
        }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".col-xs-6.col-sm-4.col-md-3.col-lg-3"):
            book_page = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(book_page, callback=self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
