import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            book_url = response.urljoin(book_url)
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("p.availability::text").re_first("\d+"),
            "rating": response.css("p.star-rating::attr(class)").re_first("star-rating (\w+)"),
            "category": response.css("ul.breadcrumb li a::text")[-2].get(),
            "description": response.css("meta[name=\"description\"]::attr(content)").get().strip(" ...more"),
            "upc": response.css("table.table-striped tr:nth-child(1) td::text").get(),
        }
