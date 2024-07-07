import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> None:
        for book in response.css("article.product_pod"):
            book_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(book_url, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book_details(self, response: Response) -> None:
        def extract_with_css(query: str) -> str:
            return response.css(query).get(default="").strip()

        title = extract_with_css("div.product_main h1::text")
        price = extract_with_css("p.price_color::text")
        amount_in_stock = (
            extract_with_css("p.instock.availability::text")
            .replace("In stock (", "")
            .replace(" available)", "")
            .strip()
        )
        rating = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (\w+)"
        )
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = (
            response.css("meta[name='description']::attr(content)")
            .get()
            .strip()
        )
        upc = response.css(
            "table.table.table-striped tr:nth-child(1) td::text"
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
