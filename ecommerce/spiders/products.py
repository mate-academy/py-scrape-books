import scrapy

from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for product in response.css(".product_pod"):
            title = product.css("a::attr(title)").get()
            price = float(
                product.css(".price_color::text").get().replace("£", "")
            )
            rating = product.css("p.star-rating::attr(class)").get().split()[1]

            detail_url = response.urljoin(
                product.css("h3 a::attr(href)").get()
            )
            yield response.follow(
                detail_url,
                callback=self.parse_product_details,
                meta={
                    "title": title,
                    "price": price,
                    "rating": rating
                }
            )

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product_details(self, response: Response) -> None:
        data = response.meta
        data.update({
            "amount_in_stock": int(
                response.css(
                    "th:contains('Availability') + td::text"
                ).get().split("(")[-1].split(" ")[0]
            ),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css("th:contains('UPC') + td::text").get()
        })
        yield data
