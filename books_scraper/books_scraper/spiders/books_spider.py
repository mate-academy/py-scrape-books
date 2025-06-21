import scrapy


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        for book in response.css("article.product_pod h3 a"):
            href = book.attrib["href"]
            yield response.follow(response.urljoin(href), callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(response.urljoin(next_page), callback=self.parse)

    def parse_book(self, response):
        def get_rating():
            classes = response.css("p.star-rating::attr(class)").get().split()
            return classes[-1] if len(classes) > 1 else None

        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("p.instock.availability::text").re_first(r"\d+"),
            "rating": get_rating(),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("div#product_description ~ p::text").get(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }
