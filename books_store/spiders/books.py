import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]

    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book in response.css("li.col-xs-6.col-sm-4.col-md-3.col-lg-3"):
            detail_page = response.urljoin(book.css("a::attr(href)").get())
            yield response.follow(detail_page, self._parse_detail_page)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_detail_page(response: Response) -> dict:
        title = response.css("div.col-sm-6.product_main h1::text").get()
        amount = response.css("p.instock.availability::text").getall()
        price = response.css("p.price_color::text").get().replace("£", "")
        striped_amount = amount[1].split("(")[1].split()[0]
        description = response.css("article.product_page p::text").getall()[10]
        rating_tag = response.css(".star-rating").get().split('"')[1]
        rating_list = {
            "star-rating One": 1,
            "star-rating Two": 2,
            "star-rating Three": 3,
            "star-rating Four": 4,
            "star-rating Five": 5,
        }
        yield {
            "title": title,
            "price": float(price),
            "amount_in_stock": int(striped_amount),
            "rating": rating_list[rating_tag],
            "category": response.css("ul.breadcrumb a::text").getall()[2],
            "description": description,
            "upc": response.css(".table.table-striped td::text").get()
        }
