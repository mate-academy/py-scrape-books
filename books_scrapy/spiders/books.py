import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    @staticmethod
    def parse_book_detail(responce: Response):
        book = responce.css(".page_inner")
        book_content = book.css(".content")

        title = book_content.css(".product_main h1::text").get() or "No title"
        price = book_content.css("p.price_color::text").get()
        price = price.replace("£", "") if price else "0.00"
        amount_in_stock = (
            book_content.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+) available\)") or "0"
        )
        rating = (
            book_content.css(
                "p.star-rating::attr(class)"
            ).re_first("star-rating (\w+)") or "No rating"
        )
        category = (
            book.css("ul.breadcrumb li:nth-child(3) a::text").get()
            or "No category"
        )
        description = (
            book_content.css("div#product_description ~ p::text").get()
            or "No description"
        )
        ups = (
            book_content.css(
                "table.table-striped tr:nth-child(1) td::text"
            ).get() or "No UPS"
        )

        if description.endswith(" ...more"):
            description = description[:-7]

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "ups": ups,
        }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_detail_url = response.urljoin(
                book.css("h3 a::attr(href)").get()
            )
            yield scrapy.Request(
                url=book_detail_url, callback=self.parse_book_detail
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
