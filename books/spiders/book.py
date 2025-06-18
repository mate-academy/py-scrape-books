import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = response.urljoin(book.css("a::attr(href)").get())
            yield response.follow(book_url, callback=self._parse_single_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_single_book(self, response: Response):
        price_text = response.css('p.price_color::text').get()
        price = float(price_text.replace("£", "").strip())

        in_stock = ''.join(response.css("p.instock::text").getall()).strip()
        digits = [s for s in in_stock.split() if s.isdigit()]
        amount_in_stock = int(digits[0]) if digits else 0

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_text = rating_class.split()[-1]
        rating = self.RATING_MAP.get(rating_text, 0)

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        description = response.css("#product_description ~ p::text").get()
        if description:
            description = description.strip()

        upc = response.css("table.table tr:nth-child(1) td::text").get()

        item = BooksItem()
        item['title'] = response.css(".product_main h1::text").get()
        item['price'] = price
        item['amount_in_stock'] = amount_in_stock
        item['rating'] = rating
        item['category'] = category
        item['description'] = description
        item['upc'] = upc

        yield item
