import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        book_urls = response.css(".image_container > a::attr(href)").getall()
        for book_url in book_urls:
            book_url = response.urljoin(book_url)
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        yield {
            "title": response.css(".product_page h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.css(
                ".instock.availability::text"
            ).re_first(r"\((\d+) available\)"),
            "rating": rating_map[
                response.css(".star-rating::attr(class)").get().split()[-1]
            ],
            "category": response.css(".page ul a::text").extract()[2],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table-striped td::text").get(),
        }

        next_page = response.css(".pager > li > a::attr(href)").get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)
