import re
import scrapy

from books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = self._clean(response.css("div.product_main h1::text").get())

        price = self._clean(response.css("div.product_main p.price_color::text").get())

        availability_text = " ".join(
            [t.strip() for t in response.css("p.instock.availability *::text").getall() if t.strip()]
        )
        amount_in_stock = self._parse_stock(availability_text)

        rating = self._parse_rating(response)

        category = self._parse_category(response)

        description = response.xpath(
            '//div[@id="product_description"]/following-sibling::p[1]/text()'
        ).get()
        description = self._clean(description)

        upc = response.xpath(
            '//table[contains(@class,"table")]//tr[th[normalize-space()="UPC"]]/td/text()'
        ).get()
        upc = self._clean(upc)

        item = BooksScraperItem()

        item["title"] = title
        item["price"] = price
        item["amount_in_stock"] = amount_in_stock
        item["rating"] = rating
        item["category"] = category
        item["description"] = description
        item["upc"] = upc

        yield item


    def _clean(self, value):
        if value is None:
            return None
        value = value.strip()
        return value if value else None

    def _parse_stock(self, text):
        if not text:
            return 0

        m = re.search(r"\((\d+)\s+available\)", text)
        return int(m.group(1)) if m else 0

    def _parse_rating(self, response):
        classes = response.css("div.product_main p.star-rating::attr(class)").get() or ""
        parts = classes.split()
        rating_word = next((p for p in parts if p in self.RATING_MAP), None)
        return self.RATING_MAP.get(rating_word)

    def _parse_category(self, response):
        crumbs = [c.strip() for c in
                  response.css("ul.breadcrumb li a::text").getall() if
                  c.strip()]
        return crumbs[-1] if crumbs else None
