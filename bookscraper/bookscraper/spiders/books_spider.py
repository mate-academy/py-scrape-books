import scrapy
from bookscraper.items import BookItem
from decimal import Decimal

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            book_url = response.urljoin(link)
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book(self, response):
        item = BookItem()

        item["title"] = response.css("div.product_main h1::text").get()

        raw_price = response.css("div.product_main p.price_color::text").get()
        clean_price = raw_price.replace("£", "").strip() if raw_price else "0"
        item["price"] = float(Decimal(clean_price))

        stock_text = response.css("div.product_main p.instock.availability::text").re_first(r"\((\d+)\s+available\)")
        item["amount_in_stock"] = int(stock_text) if stock_text else 0

        rating_classes = response.css("div.product_main p.star-rating::attr(class)").get()
        rating = 0
        if rating_classes:
            for cls in rating_classes.split():
                if cls in self.RATING_MAP:
                    rating = self.RATING_MAP[cls]
                    break
        item["rating"] = rating

        breadcrumb_links = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = breadcrumb_links[2].strip() if len(breadcrumb_links) > 2 else ""

        description = response.css("div#product_description ~ p::text").get()
        item["description"] = description.strip() if description else ""

        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()
        item["upc"] = upc.strip() if upc else ""

        yield item
