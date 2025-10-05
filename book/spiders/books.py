import re
import scrapy
from scrapy.http import Response
from book.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        categories = response.css("div.side_categories ul li ul li a")
        for cat in categories:
            category_name = cat.css("::text").get(default="").strip()
            category_url = response.urljoin(cat.attrib["href"])
            yield scrapy.Request(
                category_url,
                callback=self.parse_category,
                cb_kwargs={"category": category_name},
            )

    def parse_category(self, response: Response, category):
        books = response.css("article.product_pod h3 a::attr(href)").getall()
        for book in books:
            yield response.follow(
                book,
                callback=self.parse_book,
                cb_kwargs={"category": category}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category,
                cb_kwargs={"category": category}
            )

    def parse_book(self, response: Response, category):
        stock_text = ''.join(response.css("p.instock.availability::text").getall()).strip()
        amount_match = re.search(r"\d+", stock_text)
        amount_in_stock = int(amount_match.group()) if amount_match else 0

        rating_class = response.css("p.star-rating::attr(class)").get(default="")
        rating = rating_class.replace("star-rating", "").strip()

        description = response.css("#product_description ~ p::text").get(default="")
        upc = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get(default="")

        yield BookItem(
            title=response.css("div.product_main h1::text").get(default=""),
            price=response.css("p.price_color::text").get(default=""),
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc,
        )
