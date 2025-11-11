import re
import scrapy
from scrapy.http import Response

from books.items import BookItem


def safe_get_text(selector, default=""):
    if selector is None:
        return default
    if hasattr(selector, "get"):
        val = selector.get()
    else:
        val = selector
    return val.strip() if isinstance(val, str) else default


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs):
        for book_sel in response.css("article.product_pod h3 a"):
            yield response.follow(book_sel.attrib.get("href"), callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        item = BookItem()

        item["title"] = safe_get_text(response.css("div.product_main h1::text"))
        item["price"] = safe_get_text(response.css("p.price_color::text"))

        availability_text = " ".join(response.css("p.availability::text").getall()).strip()

        match = re.search(r"\((\d+)\s+available\)", availability_text)
        item["amount_in_stock"] = int(match.group(1)) if match else 0

        rating_class = response.css("p.star-rating").attrib.get("class", "")
        rating_word = next((p for p in rating_class.split() if p.lower() != "star-rating"), "")

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        item["rating"] = rating_map.get(rating_word, 0)

        crumbs = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = crumbs[-1].strip() if crumbs else ""

        desc = response.xpath('//div[@id="product_description"]/following-sibling::p[1]/text()').get()
        item["description"] = desc.strip() if desc else ""

        upc = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
        item["upc"] = upc.strip() if upc else ""

        yield item
