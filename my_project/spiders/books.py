import scrapy
import re
from my_project.items import MyProjectItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book_link in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_link, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        main = response.css("div.product_main")
        item = MyProjectItem()

        item["title"] = main.css("h1::text").get(default='')

        price_raw = main.css("p.price_color::text").get(default='0')
        try:
            item["price"] = float(re.sub(r'[^\d.]', '', price_raw))
        except (ValueError, TypeError):
            item["price"] = 0.0

        rating_class = main.css("p.star-rating::attr(class)").get()
        item["rating"] = rating_class.replace("star-rating ", "") if rating_class else ""

        stock_raw = "".join(main.css("p.instock.availability::text").getall()).strip()
        stock_match = re.search(r'(\d+)', stock_raw)
        item["amount_in_stock"] = int(stock_match.group(1)) if stock_match else 0

        item["category"] = response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(default='')

        desc = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(default='')
        item["description"] = desc.strip()

        item["upc"] = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get(default='')

        yield item
