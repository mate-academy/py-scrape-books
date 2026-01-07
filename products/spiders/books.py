import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response, **kwargs):
        for product in response.css(".product_pod"):
            urls = product.css("h3 a::attr(href)").get()
            book_url = response.urljoin(urls)

            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("h1::text").get()

        price_text = response.css(".price_color::text").get()
        price = price_text.replace("£", "") if price_text else None

        amount_in_stock = response.css(".instock::text").re_first(r'\d+')

        rating_class = response.css(".star-rating::attr(class)").get()
        rating = rating_class.split()[-1] if rating_class else None

        category_list = response.css("ul.breadcrumb li a::text").getall()
        category = category_list[-1] if category_list else None

        description = response.css("#product_description + p::text").get()
        upc = response.css(".table-striped tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
