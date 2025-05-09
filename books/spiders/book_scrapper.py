import scrapy
from scrapy.http import Response
from books.items import BooksItem

class BookScrapperSpider(scrapy.Spider):
    name = "book_scrapper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        books = response.css('article.product_pod')
        for book in books:
            detail_page = book.css('h3 a::attr(href)').get()
            detail_page_url = response.urljoin(detail_page)
            yield response.follow(detail_page_url, callback=self.parse_book_detail)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_detail(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        item = BooksItem()
        item['title'] = extract_with_css('div.product_main h1::text')
        item['price'] = extract_with_css('p.price_color::text')
        stock_text = extract_with_css('p.instock.availability::text')
        item['amount_in_stock'] = ''.join(filter(str.isdigit, stock_text))
        item['rating'] = response.css('p.star-rating').attrib['class'].split()[-1]
        item['category'] = response.css('ul.breadcrumb li a::text').getall()[-2]

        item['description'] = extract_with_css('#product_description ~ p::text')
        item['upc'] = response.css('table.table.table-striped tr:nth-child(1) td::text').get()

        yield item
