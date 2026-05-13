import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        book_links = response.css("h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book_page)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_page(self, response: Response, **kwargs):

        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css("p.instock.availability::text").re_first(r'\d+')),
            "rating": response.css("p.star-rating::attr(class)").re_first('star-rating (.*)'),
            "category": response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(),
            "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            "upc": response.xpath("//table[@class='table table-striped']//tr[1]/td/text()").get(),
        }
