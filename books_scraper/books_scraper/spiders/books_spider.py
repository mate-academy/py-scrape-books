import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("h1::text").get()
        price = response.css("p.price_color::text").get().replace("£","").strip()
        stock_text = response.css("p.instock.availability::text").re_first(r"\d+")
        amount_in_stock = int(stock_text) if stock_text else 0
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.split()[-1] if rating_class else "None"

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description ~ p::text".get())
        upc = response.css("table.table.table-striped tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": float(price),
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
