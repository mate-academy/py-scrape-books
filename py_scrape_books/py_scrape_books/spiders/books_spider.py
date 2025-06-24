import scrapy
from py_scrape_books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        # Ссылки на все книги на странице
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_book)

        # Переход на следующую страницу (если есть)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BookItem()

        # Заголовок книги
        item['title'] = response.css("div.product_main h1::text").get().strip()
        # Цена
        item['price'] = response.css("p.price_color::text").get().strip()
        # Количество на складе
        stock = response.css("p.availability::text").re_first(r'\d+')
        item['amount_in_stock'] = int(stock) if stock else None

        # Рейтинг (по классу)
        rating_str = response.css("p.star-rating").attrib['class'].replace('star-rating', '').strip()
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        item['rating'] = rating_map.get(rating_str)

        # Категория: второй с конца элемент в хлебных крошках
        breadcrumbs = response.css("ul.breadcrumb li a::text").getall()
        item['category'] = breadcrumbs[-2].strip() if len(breadcrumbs) >= 2 else ""

        # Описание (следующий <p> после #product_description)
        desc = response.css("#product_description ~ p::text").get()
        item['description'] = desc.strip() if desc else ""

        # UPC
        item['upc'] = response.css("table.table tr:nth-child(1) td::text").get().strip()

        yield item

