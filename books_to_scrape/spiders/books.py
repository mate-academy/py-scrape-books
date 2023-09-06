from collections.abc import generator

import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    @staticmethod
    def parse_detail_page(response: scrapy.http.Response) -> dict[str, str] | None:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(
                ".price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": response.css(
                "div.col-sm-6.product_main > p.instock.availability"
            ).re_first(
                r"\d+"
            ),
            "rating": response.css(
                ".star-rating::attr(class)"
            ).get().split()[1],
            "category": response.css(
                ".breadcrumb > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css(
                "#content_inner > article > p::text"
            ).get(),
            "upc": response.css(
                ".table.table-striped > tr:nth-child(1) > td::text"
            ).get(),
        }

    def parse(self, response: scrapy.http.Response, **kwargs) -> generator:
        detail_links_per_page = response.css(
            ".image_container > a::attr(href)"
        ).getall()
        for link in detail_links_per_page:
            yield response.follow(link, callback=self.parse_detail_page)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
