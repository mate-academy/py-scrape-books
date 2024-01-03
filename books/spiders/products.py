import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):
            detailed_url = response.urljoin(product.css("h3 a::attr(href)").get())
            yield response.follow(
                detailed_url,
                callback=self._parse_detailed_page,
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_detailed_page(response: Response):
        yield {
            "title": response.css("h3 a::attr(title)").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": response.css(".instock")
            .get()
            .split()[-3]
            .replace("(", ""),
            "rating": response.css("p.star-rating").attrib["class"].split()[-1],
            "category": response.css(
                ".breadcrumb > li:nth-last-child(2) > a::text"
            )
            .get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css(
                'table.table.table-striped th:contains("UPC") + td::text'
            )
            .get(),
        }
