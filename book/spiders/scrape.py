import scrapy
from scrapy.http import Response
from typing import Generator


class Scrape(scrapy.Spider):
    name = "scrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books_1/index.html"
    ]

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]:
        book_links = response.css('h3 a::attr(href)').extract()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator[dict, None, None]:
        title: str = response.css('h1::text').get()
        price: str = response.css('.price_color::text').get(default='').lstrip('£')
        stock: str = response.css('p.availability::text').re_first(r'\d+', default='0')
        rating: str = response.css('.star-rating::attr(class)').get().split()[-1]
        category: str = response.css('.breadcrumb li a::text').getall()[-1]
        description: str = response.css('meta[name="description"]::attr(content)').get()
        upc: str = response.css('tr:nth-child(1) td::text').get()

        yield {
            'title': title,
            'price': price,
            'amount_in_stock': stock,
            'rating': rating,
            'category': category,
            'description': description,
            'UPC': upc
        }
