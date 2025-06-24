import scrapy
from py_scrape_books.items import BookItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        # ссылки на книги
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_book)
        # пагинация
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BookItem()
        item['title'] = response.css("div.product_main h1::text").get().strip()
        item['price'] = response.css("p.price_color::text").get().strip()
        stock = response.css("p.availability::text").re_first(r'\d+')
        item['amount_in_stock'] = int(stock) if stock else None

        # рейтинг
        rating_str = response.css("p.star-rating").attrib['class'].replace('star-rating', '').strip()
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        item['rating'] = rating_map.get(rating_str)

        # категория (берем 3-й элемент хлебных крошек)
        item['category'] = response.css("ul.breadcrumb li a::text").getall()[-1].strip()

        # описание (следующий параграф после h2 'Product Description')
        desc = response.css("#product_description ~ p::text").get()
        item['description'] = desc.strip() if desc else ""

        # upc
        item['upc'] = response.css("table.table tr:nth-child(1) td::text").get().strip()

        yield item
