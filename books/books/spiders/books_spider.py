import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse_end_page(self, response: Response) -> dict:

        return {
            "title":
                response.css("div.product_main h1::text").get(),
            "price":
                response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock":
                response.css("p.instock.availability").
                re_first(r"\((\d+) available\)"),
            "rating":
                response.css("p.star-rating::attr(class)").get().split()[-1],
            "category":
                response.css("ul.breadcrumb li:nth-of-type(3) a::text").
                get(),
            "description":
                response.css("#product_description + p::text").get(),
            "upc":
                response.css("table.table-striped tr:nth-child(1) td::text").
                get()
        }

    def parse(self, response: Response, **kwargs) -> None:
        current_page = response.css("ol.row li")
        next_page = response.css(".next").css("a::attr(href)").get()
        full_next_page = response.urljoin(next_page)
        print(f"Next page: {full_next_page}")

        for li in current_page:
            relative_url = li.css("a::attr(href)").get()
            book_url = response.urljoin(relative_url)

            yield scrapy.Request(book_url, callback=self.parse_end_page)

        if next_page is not None:
            yield scrapy.Request(full_next_page, callback=self.parse)
