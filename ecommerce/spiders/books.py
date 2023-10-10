import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs) -> None:
        for book_url in response.css("h3 a::attr(href)").extract():
            yield response.follow(book_url, self.parse_book)

    def parse_book(self, response: Response) -> dict:
        rating_text = response.css(
            ".star-rating::attr(class)"
        ).get().split(" ")[-1]
        for book in response.css(".product_pod"):
            yield {
                "title": book.css("h3 > a::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text"
                             ).get().replace("£", "")),
                "amount_in_stock": int(
                    response.css("p.availability::text"
                                 ).re_first(r"\d+")),
                "rating": self.RATING.get(rating_text),
                "category": response.css(
                    ".breadcrumb > li > a[href*='category/books/']::text"
                ).get().strip(),
                "description": response.css(
                    "meta[name='description']::attr(content)"
                ).get(),
                "upc": response.css("th:contains('UPC') + td::text").get(),
            }

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
