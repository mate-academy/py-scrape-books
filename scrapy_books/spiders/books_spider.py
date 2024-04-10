import scrapy
import re


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/",
    ]

    def parse(self, response, **kwargs):
        books_urls = []
        for product in response.css("ol > li > article"):
            books_urls.append(product.css("a::attr(href)").get())
        next_page_url = response.css(
            "ul > li.next > a::attr(href)"
        ).extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))
        for book_url in books_urls:
            yield scrapy.Request(
                response.urljoin(book_url), callback=self.parse_book
            )

    def parse_book(self, response):
        stock = re.search(
            r"\d+",
            response.css(
                "div.col-sm-6.product_main > p.instock.availability::text"
            )[-1].get(),
        ).group()
        yield {
            "title": response.css(
                "div.col-sm-6.product_main > h1::text"
            ).extract_first(),
            "price": response.css(
                "div.col-sm-6.product_main > p.price_color::text"
            ).extract_first(),
            "amount_in_stock": stock,
            "rating": response.css(
                "div.col-sm-6.product_main > p.star-rating::attr(class)"
            )
            .extract_first()
            .split()[-1],
            "category": response.css(
                "li:nth-child(3) > a::text"
            ).extract_first(),
            "description": response.css("article > p::text").extract_first(),
            "upc": response.css("tr:nth-child(1) > td::text").extract_first(),
        }
