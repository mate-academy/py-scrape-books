import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from app.items import BookItem
from app.utils import clean_price, extract_stock_number, convert_rating


class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rules = (
        Rule(
            LinkExtractor(restrict_css=".side_categories > ul > li > ul a"), follow=True
        ),
        Rule(LinkExtractor(restrict_css=".next a"), follow=True),
        Rule(LinkExtractor(restrict_css="h3 > a"), callback="parse_book", follow=False),
    )

    def parse_start_url(self, response):
        category = response.css("h1::text").get()

        for book_url in response.css("h3 > a::attr(href)").getall():
            yield response.follow(
                book_url, self.parse_book, meta={"category": category}
            )

    def parse_book(self, response):
        item = BookItem()

        category = response.meta.get("category")
        if not category:
            category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        item["title"] = response.css("h1::text").get()
        item["category"] = category.strip() if category else None

        price = response.css("p.price_color::text").get()
        item["price"] = clean_price(price)

        stock_info = response.css("p.instock.availability::text").getall()
        stock_text = " ".join([s.strip() for s in stock_info if s.strip()])
        item["amount_in_stock"] = extract_stock_number(stock_text)

        rating_class = response.css("p.star-rating::attr(class)").get()
        item["rating"] = convert_rating(rating_class)

        description_parts = response.css("#product_description + p::text").getall()
        item["description"] = (
            " ".join(description_parts).strip() if description_parts else None
        )

        item["upc"] = self.extract_upc(response)

        yield item

    def extract_upc(self, response):
        rows = response.css("table.table-striped tr")
        for row in rows:
            th = row.css("th::text").get()
            if th and "UPC" in th:
                return row.css("td::text").get()
        return None
