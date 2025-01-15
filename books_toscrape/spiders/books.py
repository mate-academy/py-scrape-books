import scrapy

from scrapy.http import Response
from word2number.w2n import word_to_num

from books_toscrape.items import BooksToscrapeItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_links = response.css("a[title]")

        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_detail_book_page)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail_book_page(self, response: Response) -> BooksToscrapeItem:
        yield BooksToscrapeItem(
            title=response.css(".product_main h1::text").get(),
            price=float(
                response.css(".product_main .price_color::text").get().replace("£", "")
            ),
            amount_in_stock=int(
                response.css("p.instock.availability::text").getall()[1].strip().split("(")[1].split()[0]
            ),
            rating=word_to_num(
                response.css(".product_main .star-rating::attr(class)").get().split()[-1]
            ),
            category=response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.css("table.table-striped tr:nth-child(1) td::text").get()
        )
