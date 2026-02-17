import scrapy

from book_scraper.items import BookScraperItem

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book_url in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        table = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in response.css("table.table-striped tr")
        }

        item = BookScraperItem()
        item["title"] = response.css("h1::text").get()
        item["price"] = float(
            response.css("p.price_color::text").get().replace("£", "").strip()
        )
        item["amount_in_stock"] = int(
            response.css("p.availability::text").re_first(r"\d+")
        )
        item["rating"] = RATING_MAP.get(
            response.css("p.star-rating::attr(class)").re_first(
                r"star-rating (\w+)"
            ),
            0,
        )
        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()
        item["description"] = response.css(
            "#product_description + p::text"
        ).get(default="")
        item["upc"] = table.get("UPC")

        yield item
