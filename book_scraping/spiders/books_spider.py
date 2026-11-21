import scrapy
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod h3 a")
        yield from response.follow_all(books, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css("p.availability::text").re_first(r"\d+")),
            "rating": w2n.word_to_num(response.css("p.star-rating").attrib["class"].split()[-1]),
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description": response.css("div#product_description + p::text").get(),
            "upc": response.css("table.table td::text").get(),
        }
