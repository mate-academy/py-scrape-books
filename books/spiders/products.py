from pathlib import Path

import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        filename = f"products.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")


