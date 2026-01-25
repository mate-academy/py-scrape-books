import re
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup
from ..items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # Мапа CSS-класу рейтингу → число
    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response):
        """
        Головна: проходимо всі категорії (окрім 'Books' у верхньому меню).
        """
        # Ліва панель категорій
        for href in response.css("div.side_categories ul ul li a::attr(href)").getall():
            url = urljoin(response.url, href)
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        """
        Сторінка категорії: проходимо всі книги на сторінці та пагінацію.
        """
        # Картки книжок
        for href in response.css("section div ol.row li article.product_pod h3 a::attr(href)").getall():
            url = urljoin(response.url, href)
            yield scrapy.Request(url, callback=self.parse_book)

        # Пагінація
        next_rel = response.css("li.next a::attr(href)").get()
        if next_rel:
            yield scrapy.Request(urljoin(response.url, next_rel), callback=self.parse_category)

    def parse_book(self, response):
        """
        Сторінка книги: збір усіх потрібних полів.
        """
        # Title
        title = response.css("div.product_main h1::text").get(default="").strip()

        # Price (формат '£51.77')
        raw_price = response.css("div.product_main p.price_color::text").get(default="£0")
        price = float(raw_price.replace("£", "").strip())

        # Rating (клас p.star-rating.Four → 4)
        rating_cls = response.css("div.product_main p.star-rating::attr(class)").get("")  # 'star-rating Four'
        rating_word = rating_cls.split()[-1] if rating_cls else ""
        rating = self.RATING_MAP.get(rating_word, 0)

        # Availability → amount_in_stock
        # Текст на кшталт: "In stock (22 available)"
        availability_text = " ".join(response.css("div.product_main p.availability::text").getall()).strip()
        m = re.search(r"\((\d+)\s+available\)", availability_text)
        amount_in_stock = int(m.group(1)) if m else 0

        # Category (breadcrumb: Home » Books » <Category> » Title)
        # Беремо передостанній <li> з class 'active' — ні; краще <ul.breadcrumb> li a (останній a перед active)
        breadcrumbs = response.css("ul.breadcrumb li")
        category = ""
        if len(breadcrumbs) >= 3:
            # breadcrumb: 0:Home, 1:Books, 2:Category, 3:Title(active)
            category = breadcrumbs[2].css("a::text").get(default="").strip()

        # Description
        # Опис знаходиться в #product_description + p
        desc_sel = response.css("#product_description ~ p")
        description = desc_sel[0].get() if desc_sel else ""
        if description:
            # легке очищення html → текст
            description = BeautifulSoup(description, "html.parser").get_text(" ", strip=True)

        # UPC зі специфікації
        upc = ""
        for row in response.css("table.table.table-striped tr"):
            header = row.css("th::text").get("")
            if header == "UPC":
                upc = row.css("td::text").get("").strip()
                break

        yield BookItem(
            title=title,
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc,
        )
