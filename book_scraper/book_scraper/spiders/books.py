import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "http://books.toscrape.com/catalogue/category/books_1/index.html"
    ]

    def parse(self, response: any) -> any:
        book_links = response.css(".product_pod h3 a::attr(href)").getall()
        for book_link in book_links:
            yield response.follow(book_link, self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: any) -> dict:
        yield {
            "title":
                response.css("h1::text").get(),
            "price":
                response.css(".price_color::text").get(),
            "amount_in_stock":
                response.css(".instock.availability::text").get().strip(),
            "rating":
                response.css(".star-rating::attr(class)").re_first(r"\d"),
            "category":
                response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description":
                response.css("meta[name=description]::attr(content)").get(),
            "upc":
                response.css("tr:nth-child(1) td::text").get(),
        }
