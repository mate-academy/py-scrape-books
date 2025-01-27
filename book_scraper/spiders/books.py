import scrapy
from scrapy.http import Response, Request
from urllib.parse import urljoin


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        books = response.css(".product_pod")
        for book in books:
            relative_url = book.css("a::attr(href)").get()
            if "catalogue/" in relative_url:
                book_url = urljoin("https://books.toscrape.com/", relative_url)
            else:
                book_url = book_url = urljoin(
                    "https://books.toscrape.com/catalogue/", relative_url
                )
            yield Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next a ::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        table = response.css("table tr")
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                table[5].css("td ::text").get().split()[2].lstrip("(")
            ),
            "rating": response.css(
                "p.star-rating"
            ).attrib["class"].split()[-1],
            "category": response.css(
                "ul.breadcrumb>li:nth-child(3)>a[href]::text"
            ).get(),
            "description": response.css(
                "div#product_description ~ p::text"
            ).get(),
            "upc": table[0].css("td ::text").get()
        }
