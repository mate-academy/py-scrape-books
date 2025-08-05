import scrapy
import re

from scrape_books.items import ScrapeBooksItem


class BookSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # Extract book links from the current page
        book_links = response.css('article.product_pod h3 a::attr(href)').getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        # Follow pagination link if exists
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        book = ScrapeBooksItem()
        # Extract title
        book['title'] = response.css('div.product_main h1::text').get()

        # Extract price
        book['price'] = response.css('p.price_color::text').get()

        # Extract stock amount
        stock_text = response.css('p.instock.availability ::text').getall()
        cleaned_stock_text = ' '.join([text.strip() for text in stock_text if text.strip()])
        if cleaned_stock_text:
            match = re.search(r'\((\d+) available\)', cleaned_stock_text)
            book['amount_in_stock'] = int(match.group(1)) if match else None
        else:
            book['amount_in_stock'] = None

        # Extract rating
        rating_class = response.css('p.star-rating::attr(class)').get()
        book['rating'] = rating_class.split()[-1] if rating_class else None

        # Extract category
        book['category'] = response.css('ul.breadcrumb li:nth-last-child(2) a::text').get()

        # Extract description
        book['description'] = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).get()

        # Extract UPC
        book['upc'] = response.xpath(
            '//th[contains(text(), "UPC")]/following-sibling::td/text()'
        ).get()

        yield book
