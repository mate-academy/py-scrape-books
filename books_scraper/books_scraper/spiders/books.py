import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()
            yield response.follow(relative_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get()

        price = response.css("p.price_color::text").get()

        stock_text = response.css("p.instock.availability::text").getall()
        stock_text = "".join(stock_text).strip()

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.split()[-1]

        category = response.css("ul.breadcrumb li a::text").getall()[2]

        description = response.css("#product_description ~ p::text").get()

        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": stock_text,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
