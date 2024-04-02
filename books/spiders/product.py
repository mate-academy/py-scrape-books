import scrapy


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response):
        product_links = response.css('h3 a::attr(href)').getall()
        for product_link in product_links:
            yield response.follow(product_link, callback=self.parse_product)

    def parse_product(self, response):
        title = response.css('div.col-sm-6.product_main h1::text').get()
        price = response.css('p.price_color::text').get().replace('£', '')
        in_stock = response.css('p.availability::text').re_first(r'\((\d+) available\)')
        description = response.css('div#product_description + p::text').get()
        rating = response.css('p.star-rating::attr(class)').re_first(r'(\w+)$')
        upc = response.css('th:contains("UPC") + td::text').get()
        category = response.css('ul.breadcrumb li:nth-last-child(2) a::text').get()

        yield {
            "title": title,
            "price": price,
            "category": category,
            "in_stock": in_stock,
            "rating": rating,
            "upc": upc,
            "description": description
        }
