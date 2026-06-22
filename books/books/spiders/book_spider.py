import scrapy

from books.items import BooksItem


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books_links = response.css(".product_pod h3 a::attr(href)").getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_book)
        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response) -> dict:
        item = BooksItem()

        rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        item["title"] = response.css(".product_main h1::text").get()
        item["price"] = response.css(".product_main .price_color::text").get()
        item["amount_in_stock"] = response.css(
            ".instock::text"
        ).re_first(r"\d+")
        rating_text = response.css(
            ".star-rating::attr(class)"
        ).re_first(r"star-rating ([A-Za-z]+)")
        if rating_text:
            item["rating"] = rating_mapping.get(rating_text, 0)
        else:
            item["rating"] = 0
        categories = response.css(".breadcrumb li a::text").getall()
        item["category"] = categories[-1] if categories else None
        item["description"] = response.css(
            "#product_description + p::text"
        ).get()
        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()

        yield item
