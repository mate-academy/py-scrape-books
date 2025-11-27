import scrapy
from books_scraper.items import BooksScraperItem
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def parse(self, response: Response) -> None:
        for book in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        item = BooksScraperItem()
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css(".price_color::text").get()

        availability_text = response.css(".availability::text").getall()
        availability_text = "".join(availability_text).strip()
        item["amount_in_stock"] = int(
            availability_text.split("(")[1].split()[0]
        ) if "(" in availability_text else 0

        rating_class = response.css("p.star-rating").attrib.get("class", "")
        item["rating"] = rating_class.split()[-1] if rating_class else ""

        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

        description = response.css("#product_description + p::text").get()
        item["description"] = description.strip() if description else ""

        upc = response.css("th:contains('UPC') + td::text").get()
        item["upc"] = upc if upc else ""

        yield item
