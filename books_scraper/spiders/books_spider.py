import scrapy
from scrapy.http import Response
from word2number import w2n

class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        book_links = response.css('article.product_pod h3 a::attr(href)').getall()
        for link in book_links:
            yield response.follow(link, self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response):
        yield {
            "title": response.css(".product_page h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+)\s"),
            "rating": w2n.word_to_num(
                response.css("p.star-rating").attrib["class"].split()[1]
            ),
            "category": response.css(
                ".breadcrumb > li a::text"
            ).getall()[2],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table-striped td::text").get()
        }
