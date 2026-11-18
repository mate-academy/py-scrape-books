import scrapy
from word2number import w2n

from py_scrape_books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for href in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        stock = response.css(
            "p.availability::text"
        ).re_first(r"\((\d+) available\)")
        amount_in_stock = int(stock) if stock else 0
        rating_raw_class = response.css(
            "p.star-rating::attr(class)"
        ).get()
        rating = rating_raw_class.split()[1] if rating_raw_class else None
        navbar = response.css("ul.breadcrumb")
        category = navbar.css("a::text").getall()
        # 3rd item is a genre (2 index)

        yield BookItem(
            title=response.css("h1::text").get(),
            price=float(response.css(
                "p.price_color::text"
            ).get().replace("£", "")),
            amount_in_stock=amount_in_stock,
            rating=w2n.word_to_num(rating),
            category=category[2],
            description=response.css("p").getall()[-1],
            upc=response.css("table").css("td::text").get(),
        )
