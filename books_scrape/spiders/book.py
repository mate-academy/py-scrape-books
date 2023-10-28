from urllib.parse import urljoin

import scrapy

from books_scrape.items import BooksScrapeItem


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    BASE_URL = "https://books.toscrape.com"
    CATALOGUE_URL = urljoin(BASE_URL, "catalogue/")

    def parse(self, response, **kwargs):
        books = response.css("article.product_pod")
        for book in books:
            relative_url = book.css("h3 a ::attr(href)").get()
            book_url = self.check_catalogue_in_url(relative_url)
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.css("li.next a ::attr(href)").get()
        if next_page is not None:
            next_page_url = self.check_catalogue_in_url(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def check_catalogue_in_url(self, url):
        if "catalogue/" in url:
            return urljoin(self.BASE_URL, url)
        return urljoin(self.CATALOGUE_URL, url)

    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        book_item = BooksScrapeItem()

        book_item["title"] = (response.css(".product_main h1::text").get(),)
        book_item["price"] = (response.css("p.price_color ::text").get(),)
        book_item["amount_in_stock"] = (table_rows[5].css("td ::text").get(),)
        book_item["rating"] = (response.css("p.star-rating").attrib["class"],)
        book_item["category"] = (
            response.xpath(
                "//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()"
            ).get(),
        )
        book_item["description"] = (
            response.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
        )
        book_item["upc"] = table_rows[0].css("td ::text").get()

        yield book_item
