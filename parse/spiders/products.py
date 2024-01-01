import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book(self, response: Response) -> None:
        title = response.css("h1::text").get()
        price = response.css(".price_color::text").get().replace("£", "")
        amount_in_stock = int(
            response.css(".instock.availability::text").re_first(r"\d+")
        )
        rating = response.css(
            "p.star-rating::attr(class)"
        ).get().split(" ")[-1].lower()
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get()
        upc = response.css("th:contains('UPC') + td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }

    def parse(self, response: Response) -> None:
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(response.urljoin(book_url),
                                 callback=self.parse_book)

        next_page = response.css(".pager > li.next > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
