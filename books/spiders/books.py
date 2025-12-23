import scrapy
from scrapy.http.response import Response
from pathlib import Path
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse_detail_page(self, response: Response):
        data =  {
            "title": response.css(".product_main h1::text").get(),
            "price": float(response.css(".product_main .price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css(".table tr:nth-child(6) td::text").get().split(" ")[2].replace("(", "")),
            "rating": w2n.word_to_num(
                response.css(".star-rating").attrib["class"].split(" ")[1]
            ),
            "category": response.css(".breadcrumb li a::text").getall()[1],
            "description": response.css(".product-description + p::text").get(),
            "upc": response.css(".table tr:first-child td::text").get()
        }
        yield data

    def parse(self, response: Response):
        for book in response.css(".product_pod"):
            details_url = book.css("h3 a::attr(href)").get()
            full_url = response.urljoin(details_url)
            yield scrapy.Request(full_url, callback=self.parse_detail_page)
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, callback=self.parse)
        filename = "books.jl"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
