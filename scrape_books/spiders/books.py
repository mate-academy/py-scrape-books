import scrapy
from scrapy.http import Response


def parse_detail_page(response: Response) -> None:
    yield {
        "title": response.css("h1::text").get(),
        "price": response.css(".price_color::text").get()[1:],
        "amount_in_stock": response.css(
            ".table td::text").getall()[5].split()[2][1:],
        "category": response.css(
            ".breadcrumb").xpath("./li/a/text()").getall()[-1],
        "rating": response.css(
            ".star-rating").xpath("@class").get().split()[1],
        "description": response.css(
            ".product_page").xpath("./p/text()").get(),
        "upc": response.css(".table td::text").getall()[0]
    }


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        urls_on_page = response.css(
            "ol.row .image_container a::attr(href)"
        ).getall()
        next_page = response.css("li.next a::attr(href)").get()
        for url in urls_on_page:
            url_full = response.urljoin(url)
            yield scrapy.Request(url_full, parse_detail_page)

        url_next_page = response.urljoin(next_page)
        yield scrapy.Request(url_next_page, self.parse)
