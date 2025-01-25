import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        detail_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()
        for link in detail_links:
            yield response.follow(link, self.parse_detail)

        next_page_url = response.css("li.next > a::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    @staticmethod
    def parse_detail(response: Response):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css(
                "div.product_main p.price_color::text"
            ).get(),
            "amount_in_stock": "".join(
                response.css(
                    "div.product_main p.availability.instock::text"
                ).getall()
            ).strip(),
            "rating": response.css(
                "div.product_main p.star-rating::attr(class)"
            )
            .get()
            .split()[-1],
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            "upc": response.css("table tr:nth-child(1) td::text").get(),
        }
