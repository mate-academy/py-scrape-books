import scrapy
from scrapy.http import Response
from scrapy.selector import SelectorList

from py_scrape_books.items import PyScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: SelectorList, **kwargs) -> {}:
        for quote in response.css(".product_pod"):
            absolute_url = response.urljoin(
                quote.css("h3 a::attr(href)").get()
            )
            yield scrapy.Request(
                url=absolute_url,
                callback=self._parse_page_book_detail
            )

        next_page = response.css(".next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_rating(self, response: Response) -> str:
        stars = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        classes = response.css(".star-rating").xpath("@class").extract()
        return stars[classes[0].split()[1]]

    def _parse_page_book_detail(self, response: Response) -> dict:
        in_stock = False
        if response.css(".icon-ok").get():
            in_stock = True

        yield PyScrapeBooksItem(
            title=response.css("h1::text").get(),
            price=response.css(".price_color::text").get(),
            amount_in_stock=(
                int(
                    response.css(".instock")
                    .get()
                    .split(" ")[21].replace("(", "")
                )
                if in_stock
                else 0
            ),
            rating=self._get_rating(response),
            category=response.css(".breadcrumb li a::text").getall()[2],
            description=response.css("#product_description + *::text").get(),
            upc=response.css("td::text").get(),
        )
