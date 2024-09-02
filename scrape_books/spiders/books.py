import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books_detailed = []
        for product in response.css(".product_pod"):
            books_detailed += [product.css("h3 > a::attr(href)").get()]

        for book_detailed in books_detailed:
            book_detailed_url = response.urljoin(book_detailed)
            yield scrapy.Request(
                book_detailed_url, callback=self._parse_detailed_book_page
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_detailed_book_page(self, response: Response, **kwargs):
        rating_classes = {
            "Five": 5,
            "Four": 4,
            "Three": 3,
            "Two": 2,
            "One": 1,
            "Zero": 0,
        }
        return {
            "title": response.css(".breadcrumb > li")[3].css("::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".instock.availability")[0]
                .css("::text")
                .getall()[1]
                .strip()
                .split("(")[1]
                .split()[0]
            ),
            "rating": rating_classes[
                response.css(".star-rating::attr(class)").get().split()[1]
            ],
            "category": response.css(".breadcrumb > li")[2]
            .css("a::text")
            .get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(".table > tr > td::text").getall()[0],
        }
