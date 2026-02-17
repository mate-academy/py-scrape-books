import re
import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get()
        price = response.css("p.price_color::text").get()

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.split()[-1] if rating_class else None

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        description = response.css("#product_description + p::text").get()

        upc = response.xpath(
            "//th[normalize-space()='UPC']/following-sibling::td/text()"
        ).get()

        availability_text = response.css("p.availability::text").getall()
        availability_text = " ".join(t.strip() for t in availability_text if t.strip())

        match = re.search(r"\((\d+) available\)", availability_text)
        amount_in_stock = int(match.group(1)) if match else None

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
