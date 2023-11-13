import scrapy
from scrapy.http import Response

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def _parse_book_info(response: Response) -> dict:
        book = response.css(".product_page")

        return {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(
                book.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                book.css("p.instock::text").re(r"\d+").pop()
            ),
            "rating": RATINGS[
                book.css(".star-rating::attr(class)").get().split().pop()
            ],
            "category": response.css(".breadcrumb > li > a[href]::text")
            .getall()
            .pop(),
            "description": response.css(".product_page > p::text").get(),
            "upc": book.css('th:contains("UPC") + td::text').get(),
        }

    def parse(self, response: Response, **kwargs) -> dict:
        books_urls = response.css(".product_pod > h3 > a::attr(href)").getall()

        for url in books_urls:
            yield scrapy.Request(
                response.urljoin(url), callback=self._parse_book_info
            )

        if next_page := response.css(".next > a::attr(href)").get():
            yield response.follow(next_page, callback=self.parse)
