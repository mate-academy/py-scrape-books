import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    rating = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse_single_book(self, response: Response) -> dict:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get()[1:]),
            "amount_in_stock": int(
                response.css("p.instock::text").re_first(r"\d+")
            ),
            "rating": self.rating[
                response.css(".star-rating::attr(class)").get().split(" ")[1]
            ],
            "category": response.css(
                ".breadcrumb > li"
            )[2].css("a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css('th:contains("UPC") + td::text').get()
        }

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            book_url = book.css(".image_container > a[href]::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_single_book)

        next_page = response.css(".next > a[href]::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
