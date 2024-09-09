import scrapy
from scrapy.http import Response


class AllBooksSpider(scrapy.Spider):
    name = "all_books"
    allowed_domains = ["books.toscrape.com"]
    BASE_URL = "https://books.toscrape.com/catalogue/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(f"{self.BASE_URL}/page-1.html", callback=self.parse)

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            yield response.follow(
                f"{self.BASE_URL}{book.css('h3 > a::attr(href)').get()}",
                self.parse_detailed
            )

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(
                next_page_url,
                self.parse
            )


    @staticmethod
    def parse_detailed(response: Response, **kwargs):
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(
                    ".product_main > p.price_color::text"
                ).get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(
                    ".product_main > p.instock"
                ).re_first(r"\d+")
            ),
            "rating": response.css(
                ".product_main > p.star-rating::attr(class)"
            ).get().split()[1],
            "category": response.css(
                ".breadcrumb > li"
            )[2].css("a::text").get(),
            "description": response.css(
                ".product_page > p::text"
            ).get(),
            "upc": response.css(
                ".table tr"
            )[0].css("td::text").get()
        }

