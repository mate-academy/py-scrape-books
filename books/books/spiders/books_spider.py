import scrapy
from scrapy.http import Response


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".image_container *::attr(href)")
        yield from response.follow_all(book_page_links, self._parse_book)

        pagination_links = response.css("li.next > a::attr(href)")
        yield from response.follow_all(pagination_links, self.parse)


    def _parse_book(self, response: Response):
        yield {
            "title": response.css(".product_main > h1::text").get().strip(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css(".table-striped > tr > td::text").getall()[-2].split()[-2][1:]),
            "rating": RATING_MAP.get(response.css(".star-rating::attr(class)").get().split()[-1], 0),
            "category": response.css(".breadcrumb > li > a::text")[2].get().strip(),
            "description": response.css(".product_page > p::text").get().strip(),
            "upc": response.css(".table-striped > tr > td::text").get().strip(),
        }
