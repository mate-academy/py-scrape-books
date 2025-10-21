import scrapy
from scrapy.http import Response


class BookItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    amount_in_stock = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    upc = scrapy.Field()


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response):
        for book_url in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        item = BookItem()

        item["title"] = (
            response.css("div.product_main h1::text").get(default="").strip()
        )
        item["price"] = response.css("p.price_color::text").get(default="").strip()

        stock_text = response.css("p.instock.availability::text").getall()
        stock_clean = [t.strip() for t in stock_text if t.strip()]
        item["amount_in_stock"] = (
            int(response.css("p.instock.availability").re_first(r"\d+"))
            if stock_clean
            else 0
        )

        rating_class = response.css("p.star-rating::attr(class)").get(default="")
        rating_word = rating_class.replace("star-rating", "").strip()
        item["rating"] = self.RATING_MAP.get(rating_word, None)

        item["category"] = (
            response.css("ul.breadcrumb li:nth-child(3) a::text")
            .get(default="")
            .strip()
        )

        desc = response.css("#product_description ~ p::text").get()
        item["description"] = desc.strip() if desc else ""

        item["upc"] = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get(default="")

        yield item
