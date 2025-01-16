import scrapy
from books.items import BooksItem


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # Extract book URLs from the current page
        books = response.css('article.product_pod h3 a::attr(href)').getall()
        for book_url in books:
            yield response.follow(book_url, self.parse_book)

        # Follow pagination links
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BooksItem()
        item['title'] = response.css('div.product_main h1::text').get()
        item['price'] = response.css('p.price_color::text').get()
        stock_text = response.css('p.instock.availability::text').getall()
        item['amount_in_stock'] = ''.join(stock_text).strip()
        rating_class = response.css('p.star-rating').attrib.get('class')
        item['rating'] = rating_class.replace('star-rating', '').strip()
        item['category'] = response.css('ul.breadcrumb li a::text').getall()[-1]
        item['description'] = response.css('#product_description ~ p::text').get()
        item['upc'] = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
        yield item
