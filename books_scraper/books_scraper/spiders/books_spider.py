from typing import Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    start_urls = ['https://books.toscrape.com/']

    def parse(self, response: Response, **kwargs: Any):
        book_urls = response.css('article.product_pod h3 a::attr(href)').getall()
        for url in book_urls:
            yield response.follow(url, callback=self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book(response):
        title = response.css('h1::text').get()
        price = response.css('p.price_color::text').get()
        amount_in_stock = response.css('p.instock.availability::text').re_first('\d+')
        rating = response.css('p.star-rating::attr(class)').get().split()[-1]
        category = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        description = response.css('meta[name="description"]::attr(content)').get().strip()
        upc = response.css('table.table tr:nth-child(1) td::text').get()

        yield {
            'title': title,
            'price': price,
            'amount_in_stock': amount_in_stock,
            'rating': rating,
            'category': category,
            'description': description,
            'upc': upc
        }
