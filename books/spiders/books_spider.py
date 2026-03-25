import scrapy
from books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"

    start_urls = [
        "https://books.toscrape.com/",
    ]

    def parse(self, response):
        book_page_links = response.css("article.product_pod a")
        yield from response.follow_all(book_page_links, callback=self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    def parse_book(self, response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        yield BookItem(
            title=extract_with_css("div.product_main h1::text"),
            price=extract_with_css("div.product_main .price_color::text"),  # строка!
            amount_in_stock=response.css("p.instock.availability::text").getall(),
            rating=response.css(".star-rating::attr(class)").get(default=""),
            category=response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            description=extract_with_css("#product_description + p::text"),
            upc=response.xpath("//th[text()='UPC']/following-sibling::td/text()").get(
                default=""
            ),
        )
