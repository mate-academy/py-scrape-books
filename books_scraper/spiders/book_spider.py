import scrapy


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        book_urls = response.css('article.product_pod h3 a::attr(href)').getall()

        for url in book_urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_book(self, response):
        title = response.css('div.product_main h1::text').get()

        price = response.css('p.price_color::text').get()

        amount_in_stock = response.xpath('//th[text()="Availability"]/following-sibling::td/text()').re_first(r'\d+')

        amount_in_stock = int(amount_in_stock) if amount_in_stock else 0

        rating = response.css('p.star-rating::attr(class)').get()
        if rating:
            rating = rating.replace('star-rating ', '')

        category = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        if category:
            category = category.strip()

        description = response.css('#product_description + p::text').get()

        upc = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()

        yield {
            'title': title,
            'price': price,
            'amount_in_stock': amount_in_stock,
            'rating': rating,
            'category': category,
            'description': description,
            'upc': upc
        }
