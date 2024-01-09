import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("section ol.row li"):
            book_link = book.css("h3 a::attr(href)").get()
            book_detail_link = response.urljoin(book_link)
            yield response.follow(book_detail_link, callback=parse_single_book)
        next_page = (
            response.css("section ul.pager li.next").css("a::attr(href)").get()
        )
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


def parse_single_book(response: Response) -> dict:
    book = response.css(".page_inner")
    return {
        "title": book.css("h1::text").get(),
        "price": float(book.css(".price_color::text").get()[1:]),
        "amount_in_stock": int(book.css(".instock").get().split()[-3][1:]),
        "rating": book.css(".star-rating::attr(class)").get().split()[1],
        "category": response.css(".breadcrumb li a::text").getall()[2],
        "description": response.css(".product_page > p::text").get(),
        "upc": response.css("table td::text").get(),
    }
