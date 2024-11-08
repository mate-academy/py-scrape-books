import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_list = response.css(".product_pod")
        for book in book_list:
            url = book.css("h3 a::attr(href)").get()
            yield response.follow(url, self.parse_single_book)

        next_page = response.urljoin(response.css(".next a::attr(href)").get())
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".availability::text").re_first(r'\d+'),
            "rating": response.css(".star-rating::attr(class)").re_first(r"star-rating (\w+)"),
            "category": response.css(".breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description ~ p::text").get(),
            "upc": response.css("table.table-striped tr:nth-child(1) td::text").get(),
        }
