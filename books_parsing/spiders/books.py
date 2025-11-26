import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # Helper: safe .get()
    def safe_get(self, selector, default=None):
        value = selector.get()
        return value if value is not None else default

    def parse(self, response: Response):
        for book in response.css("article.product_pod"):
            book_link = book.css("h3 a::attr(href)").get()
            url = response.urljoin(book_link)

            yield scrapy.Request(url, callback=self.parse_book_info)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_info(self, response: Response):
        price_raw = self.safe_get(response.css(".price_color::text"))
        rating_raw = self.safe_get(response.css("p.star-rating::attr(class)"))
        category_raw = self.safe_get(response.css("ul.breadcrumb li:nth-child(3) a::text"))

        # Sanitize values if not missing
        price = price_raw.replace("£", "") if price_raw else None
        rating = (
            rating_raw.replace("star-rating", "").strip()
            if rating_raw else None
        )

        yield {
            "title": self.safe_get(response.css(".product_main h1::text")),
            "price": price,
            "amount_in_stock": response.css(".instock.availability::text")
                                      .re_first(r'\d+') or None,
            "rating": rating,
            "category": category_raw,
            "description": self.safe_get(response.css("#product_description ~ p::text")),
            "upc": self.safe_get(response.css("table tr:nth-child(1) td::text")),
        }
