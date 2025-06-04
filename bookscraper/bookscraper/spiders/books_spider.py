from urllib.parse import urljoin

import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response: scrapy.http.Response) -> None:
        category_urls = response.css(
            "div.side_categories ul li ul li a::attr(href)"
        ).getall()
        for url in category_urls:
            absolute_url = urljoin(response.url, url)
            yield scrapy.Request(absolute_url, callback=self.parse_category)

    def parse_category(self, response: scrapy.http.Response) -> None:
        book_urls = response.css("h3 a::attr(href)").getall()
        for url in book_urls:
            absolute_url = urljoin(response.url, url)
            yield scrapy.Request(absolute_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            absolute_url = urljoin(response.url, next_page)
            yield scrapy.Request(absolute_url, callback=self.parse_category)

    def parse_book(self, response: scrapy.http.Response) -> None:
        table_rows = response.css("table tr")
        availability_text = response.css(
            "p.instock.availability::text"
        ).getall()
        availability_cleaned = "".join(availability_text).strip()

        import re

        match = re.search(r"\((\d+) available\)", availability_cleaned)
        amount_in_stock = int(match.group(1)) if match else 0

        book_data = {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": amount_in_stock,
            "rating": response.css(
                "p.star-rating::attr(class)"
            ).get().split()[-1],
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.xpath(
                '//div[@id="product_description"]/following-sibling::p/text()'
            ).get(),
            "upc": table_rows[0].css("td::text").get(),
        }
        yield book_data
