import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        all_page_books = response.css(
            ".image_container > a::attr(href)"
        ).getall()
        for book in all_page_books:
            detail_page = response.urljoin(book)
            yield scrapy.Request(detail_page, callback=self.get_books_detail_info)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)

    @staticmethod
    def get_books_detail_info(response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".availability").get().split()[7].replace("(", "")
            ),
            "rating": response.css(
                ".star-rating").get().split()[2].replace('">', ""),
            "category": response.css(
                ".breadcrumb > li > a").getall()[-1].split(">")[-2].replace("</a", ""),
            "description": response.css(".sub-header + p::text").get(),
            "UPC": response.css(".table > tr > td::text").get(),
           }
