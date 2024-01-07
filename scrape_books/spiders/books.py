import scrapy
from scrapy.http import Response

from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"

    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book_href in response.css(
                ".product_pod > h3 > a::attr(href)"
        ).getall():
            yield scrapy.Request(
                url=response.urljoin(book_href),
                callback=self._parse_single_book
            )

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_single_book(self, response: Response) -> dict:
        return {
            "title": response.css("div.product_main > h1::text").get(),
            "price": float(
                response.css("div.product_main p.price_color::text")
                .get()
                .replace("£", "")
            ),
            "amount_in_stock": int(
                "".join(
                    num
                    for num in response.css(
                        "div.product_main > p.availability"
                    ).get()
                    if num.isdigit()
                )
            ),
            "rating": w2n.word_to_num(
                response.css("div.product_main > p::attr(class)")
                .getall()[-1]
                .split()[-1]
            ),
            "category": response.css(
                "div.page_inner > ul.breadcrumb > li > a::text"
            ).getall()[-1],
            "description": response.css(
                "article.product_page > p::text"
            ).get(),
            "upc": response.css("th:contains('UPC') + td::text").get(),
        }
