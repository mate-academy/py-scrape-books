import scrapy
import re

class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # 1. Знаходимо всі посилання на детальні сторінки книг на поточній сторінці
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            # Використовуємо callback для переходу на сторінку книги
            yield response.follow(link, callback=self.parse_book_details)

        # 2. Пагінація: шукаємо посилання на наступну сторінку
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        # Допоміжна функція для отримання значень з таблиці характеристик
        def get_table_value(label):
            return response.xpath(f"//th[contains(text(), '{label}')]/following-sibling::td/text()").get()

        # Мапа для конвертації текстового рейтингу в число
        rating_map = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        raw_rating = response.css("p.star-rating::attr(class)").get()
        rating_text = raw_rating.replace("star-rating ", "") if raw_rating else None

        # Очищення кількості в наявності (extracting number from "In stock (19 available)")
        stock_text = get_table_value("Availability")
        amount_in_stock = int(re.findall(r'\d+', stock_text)[0]) if stock_text else 0

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": amount_in_stock,
            "rating": rating_map.get(rating_text, 0),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            "upc": get_table_value("UPC"),
        }
