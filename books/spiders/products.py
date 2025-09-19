import scrapy
from scrapy.http import Response

WORD2NUM = {'One':1,'Two':2,'Three':3,'Four':4,'Five':5}

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]


    def parse(self, response: Response, **kwargs):

        for href in response.css('.side_categories ul li ul li a::attr(href)').getall():
            yield response.follow(href, callback=self.parse_category)

    def parse_category(self, response):
        category = (response.css('.breadcrumb li.active::text').get() or '').strip()
        for product in response.css('article.product_pod'):

            title = product.css('h3 a::attr(title)').get()
            price = float(product.css('.price_color::text').get().replace("£", ""))
            rating = WORD2NUM.get(
                (product.css('.star-rating::attr(class)').get() or '').split()[-1], 0
            )
            href = product.css('h3 a::attr(href)').get()


            yield response.follow(
                href, callback=self.parse_book,
                cb_kwargs={"item": {"category": category, "title": title, "price": price, "rating": rating}})

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)


    def parse_book(self, response, item):
        item["description"] = response.css('#product_description ~ p::text').get()
        item["upc"] = response.css('th:contains("UPC") + td::text').get()
        item["amount_in_stock"] = response.css('th:contains("Availability") + td::text').get().split()[2][1:]
        yield item


