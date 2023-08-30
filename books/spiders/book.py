import scrapy
from scrapy.http import Response

from books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books_1/index.html"
    ]

    def parse(self, response: Response, **kwargs):
        for book_link in response.css("h3 > a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin(book_link),
                callback=self.parse_book
            )

        next_page = response.css("li.next > a::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

    def parse_book(self, response):
        item = BookItem()
        item["title"] = response.css("h1::text").extract_first()
        item["price"] = response.css("p.price_color::text").extract_first()
        item["amount_in_stock"] = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        item["rating"] = self.rating_from_word_to_number(
            response.css(
                "p.star-rating::attr(class)"
            ).re_first(r"star-rating (\w+)")
        )
        item["category"] = response.css(
            "ul.breadcrumb > li:nth-child(3) > a::text"
        ).extract_first()
        item["description"] = response.css(
            "meta[name='description']::attr(content)"
        ).extract_first().strip()
        item["upc"] = response.css("td::text").get()
        yield item

    @staticmethod
    def rating_from_word_to_number(word) -> int:
        return {
            "One": 1,
            "Two": 2,
            "Tree": 3,
            "Four": 4,
            "Five": 5
        }[word]
