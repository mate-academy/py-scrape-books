import scrapy
from scrapy.http import Response

from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):

            detail_book_url = response.urljoin(product.css(".image_container").css("a::attr(href)").get())
            book = ScrapeBooksItem()

            yield response.follow(
                detail_book_url,
                callback=self.parse_single_book,
                cb_kwargs={"book": book}
            )

            next_page = response.css(".next").css("a::attr(href)").get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response, book):
        for mark in (".One", ".Two", ".Three", ".Four", ".Five"):
            try:
                response.css(mark)
            except Exception:
                rating = None
            else:
                rating = mark[1:]

        book["title"] = response.css(".product_main").css("h1::text").get(),
        book["price"] = float(response.css(".price_color::text").get()[1:])
        book["amount_in_stock"] = int(response.css(".availability").get().split(" ")[-6][1:])
        book["category"] = response.css(".breadcrumb").css("a::text").getall()[2]
        book["description"] = response.css("p").getall()[3]
        book["upc"] = response.css(".table").css("td::text").get()
        book["rating"] = rating

        yield book
