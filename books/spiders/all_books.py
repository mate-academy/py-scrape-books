import scrapy
from scrapy.http import Response
from word2number import w2n

from books.items import BookItem


class AllBooksSpider(scrapy.Spider):
    name = "all_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book(self, response: Response) -> BookItem:
        return BookItem(
            title=response.css("h1::text").get(),
            price=float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            amount_in_stock=int(
                "".join(response.css(
                    "div.product_main .instock::text"
                ).getall()).strip().split()[-2].replace("(", "")
            ),
            rating=w2n.word_to_num(
                response.css(
                    "div.product_main p[class~=star-rating]::attr(class)"
                ).get().split()[-1]
            ),
            category=response.css("ul.breadcrumb a::text").getall()[-1],
            description=response.css(
                "#content_inner > article > p::text"
            ).get(),
            upc=response.css("tr:nth-child(1) td::text").get()
        )

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail_page_url = book.css("h3 a::attr(href)").get()

            yield response.follow(detail_page_url, callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
