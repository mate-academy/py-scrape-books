import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        # Find links to each book on the page
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        # Find the link to the next page
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").re_first(r"\d+\.\d+"),
            "amount_in_stock": response.css("p.instock.availability::text").re_first(r'\((\d+) available\)'),
            "rating": response.css("p.star-rating::attr(class)").re_first("star-rating (\w+)"),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("div#product_description + p::text").get(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }




