import scrapy
from scrapy.http import Response

from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        next_page_link = response.urljoin(response.css(
            ".next > a::attr(href)"
        ).get())

        urls = response.css(".col-xs-6")
        urls = [u.css("h3 > a::attr(href)").get() for u in urls]
        print(urls)
        for url in urls:
            absolute_url = response.urljoin(url)
            yield response.follow(url=absolute_url, callback=self.parse_book)

        if next_page_link is not None:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_book(self, response: Response):
        rating = response.css("p.star-rating::attr(class)").get().split(" ")[1]
        if rating:
            if rating == "One":
                rating = 1
            elif rating == "Two":
                rating = 2
            elif rating == "Three":
                rating = 3
            elif rating == "Four":
                rating = 4
            elif rating == "Five":
                rating = 5
        book = ScrapeBooksItem()
        book["title"] = response.css("h1::text").get()
        book["price"] = response.css("p.price_color::text").get()
        book["amount_in_stock"] = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        book["rating"] = rating
        book["category"] = response.css(
            "ul.breadcrumb li a::text"
        ).getall()[2]
        book["description"] = response.css(
            ".product_page p:not([class])::text"
        ).get()
        book["upc"] = response.css(
            "table.table-striped tr td::text"
        ).get()

        yield book
