import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book_link in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(book_link, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("p.instock.availability::text").re_first("\d+"),
            "rating": response.css("p.star-rating::attr(class)").re_first("star-rating (\w+)"),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("meta[name='description']::attr(content)").get().strip(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }
