import scrapy
from scrapy.http import Response

from ..items import BookscrappingItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, *args, **kwargs) -> None:
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for url in book_links:
            yield response.follow(url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        book = BookscrappingItem()

        book['title'] = response.css("h1::text").get()

        price_text = response.css("p.price_color::text").get()
        if price_text:
            book['price'] = float(price_text.replace("£", ""))

        stock_text = "".join(response.css("p.instock.availability::text").getall()).strip()
        book['amount_in_stock'] = int(''.join(filter(str.isdigit, stock_text)))

        rating_class = response.css("p.star-rating::attr(class)").get()
        if rating_class:
            book['rating'] = self._convert_rating(rating_class.split()[-1])

        book['category'] = response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(default="Unknown")

        book['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()

        book['upc'] = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()

        yield book

    @staticmethod
    def _convert_rating(rating_text):
        ratings_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        return ratings_map.get(rating_text, 0)
