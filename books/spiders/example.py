import scrapy
from books.items import BooksItem
import re


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(url, callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        stock_text = "".join(response.css(".availability::text").getall()).strip()
        amount_in_stock = int(re.search(r"\d+", stock_text).group())

        yield BooksItem(
            title=response.css("h1::text").get(),
            price=float(response.css(".price_color::text").get().replace("£", "")),
            amount_in_stock=amount_in_stock,
            rating=response.css("p.star-rating::attr(class)").get().split()[-1],
            category=response.css("ul.breadcrumb li a::text").getall()[-1],
            description=response.css("#product_description ~ p::text").get(),
            upc=response.xpath("//th[text()='UPC']/following-sibling::td/text()").get(),
        )
