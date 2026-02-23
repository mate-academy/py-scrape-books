import scrapy
from ..items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book in response.css("article.product_pod h3 a"):
            book_url = book.attrib["href"]
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        item = BooksItem()

        item["title"] = response.css("h1::text").get()

        item["price"] = response.css("p.price_color::text").get()

        stock_text = response.css("p.instock.availability::text").getall()
        stock_text = "".join(stock_text).strip()
        item["amount_in_stock"] = int(stock_text.split("(")[-1].split()[0])

        rating_class = response.css("p.star-rating").attrib["class"]
        item["rating"] = rating_class.split()[-1]

        item["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        description = response.css("#product_description ~ p::text").get()
        item["description"] = description if description else ""

        table_rows = response.css("table.table.table-striped tr")
        for row in table_rows:
            if row.css("th::text").get() == "UPC":
                item["upc"] = row.css("td::text").get()
                break

        yield item
