import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        for book in response.css(".product_pod"):
            book_detailed_url = response.urljoin(book.css("a::attr(href)").get())
            yield scrapy.Request(book_detailed_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book(self, response):
        mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        title = response.css("h1::text").get()
        price = response.css("p.price_color::text").get()

        amount_in_stock = response.css("p.instock.availability").get()
        start = amount_in_stock.find("(") + 1
        end = amount_in_stock.find(" ", start)
        amount_in_stock = amount_in_stock[start:end]

        rating = mapping[response.css("p.star-rating::attr(class)").get().split()[-1]]
        category = response.css("ul.breadcrumb a::text").getall()[-1]
        description = response.css(".product_page > p::text").getall()[-1]
        upc = response.css("td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
