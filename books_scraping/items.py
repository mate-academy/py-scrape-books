# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScrapingItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    isbn = scrapy.Field()
    availability = scrapy.Field()
    description = scrapy.Field()

    # Example how to use
    # def parse(self, response):
    #     for book in response.css('article.product_pod'):
    #         item = BooksScrapingItem()
    #         item['title'] = book.css('h3 a::attr(title)').get()
    #         item['price'] = book.css('.price_color::text').get()
    #         yield item
