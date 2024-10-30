import scrapy
from scrapy import Request
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail_url = response.urljoin(book.css("a::attr(href)").get())
            yield Request(
                url=detail_url,
                callback=self._parse_detailed_info,
                meta={
                    "title": book.css("a::attr(title)").get(),
                    "price": float(book.css(".price_color::text").get()[1:]),
                    "rating": book.css(
                        "p.star-rating::attr(class)"
                    ).get().split()[-1]
                }
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detailed_info(self, response: Response) -> dict:
        title = response.meta["title"]
        price = response.meta["price"]
        rating = response.meta["rating"]

        amount_in_stock = int(
            response.css(".instock.availability::text").re_first(r'\d+')
        )
        category = response.xpath(
            "//tr[th[text()='Product Type']]/td/text()"
        ).get()
        description = response.css("article.product_page > p::text").get()
        upc = response.xpath("//tr[th[text()='UPC']]/td/text()").get()

        yield {
            "title": title,
            "price": price,
            "rating": rating,
            "amount_in_stock": amount_in_stock,
            "category": category,
            "description": description,
            "upc": upc,
        }
