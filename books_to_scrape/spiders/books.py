import scrapy
from scrapy.http import Response

from books_to_scrape.items import BooksToScrapeItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        book_page_links = response.css(
            ".product_pod > h3 > a"
        )
        yield from response.follow_all(
            book_page_links, callback=self.parse_book
        )

        pagination_links = response.css(".next a")
        yield from response.follow_all(pagination_links, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> BooksToScrapeItem:
        rating = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

        item = BooksToScrapeItem()

        item["title"] = response.css(".product_main h1::text").get()
        item["price"] = float(
            response.css(".price_color::text").get().replace("£", "")
        )
        item["rating"] = rating[
            response.css(".star-rating::attr(class)").get().split()[-1].lower()
        ]
        item["amount_in_stock"] = int(
            response.css(".instock::text").getall()[1].strip().split()[-2][1:]
        )
        item["category"] = response.css("li:nth-last-child(2) a::text").get()
        item["description"] = response.css(".product_page > p::text").get()
        item["upc"] = response.css("tr > td::text").get()

        yield item
