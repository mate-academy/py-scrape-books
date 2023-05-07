import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response, **kwargs):
        for product in response.css("article.product_pod"):
            product_link = product.css("h3 > a::attr(href)").get()
            yield response.follow(product_link, self.parse_product)

        next_page_link = response.css("li.next > a::attr(href)").get()
        if next_page_link is not None:
            yield response.follow(next_page_link, self.parse)

    @staticmethod
    def parse_product(response):
        title = response.css("div.product_main > h1::text").get()
        price = int(
            response.css("div.product_main > p.price_color::text").re_first(
                r"\d+"
            )
        )
        amount_in_stock = int(
            response.css("div.product_main > p.availability::text").re_first(
                r"\d+"
            )
        )
        rating = response.css(
            "div.product_main > p.star-rating::attr(class)"
        ).re_first(r"star-rating (\w+)")
        rating = int(
            {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}.get(rating)
        )
        category = response.css(
            "ul.breadcrumb > li:nth-child(3) > a::text"
        ).get()
        description = response.css("article.product_page > p::text").getall()
        upc = response.css("table > tr:nth-child(1) > td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
