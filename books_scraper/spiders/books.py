import scrapy
from scrapy.http import Response

RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".product_pod h3 a")
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_book(self, response: Response, **kwargs):
        def extract_with_css(query: str):
            return response.css(query).get(default="").strip()

        def extract_all_with_css(query: str):
            return response.css(query).getall()

        yield {
            "title": extract_with_css(".product_main h1::text"),
            "price": float(extract_with_css(".price_color::text").replace("£", "")),
            "amount_in_stock": int(extract_with_css(".instock").split()[7].replace("(", "")),
            "rating": RATING.get(extract_with_css("p.star-rating::attr(class)").split()[1]),
            "category": extract_all_with_css("li > a::text")[2],
            "description": extract_with_css(".product_page > p::text"),
            "upc": extract_with_css("td::text")
        }
