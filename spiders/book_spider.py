import scrapy


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # ѕарсим ссылки на категории или страницы каталога
        for category in response.css("side_category .nav-list ul li a"):
            category_url = category.css("::attr(href)").get()
            if category_url:
                yield response.follow(category_url, callback=self.parse_category)

        # »ли обходим страницы каталога напр€мую через пагинацию
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_category(self, response):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            # ѕревращаем относительный путь в абсолютный с учетом структуры сайта
            yield response.follow(link.replace("../../../", ""), callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)

    def parse_book(self, response):
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_str = rating_class.split()[-1] if rating_class else "One"
        
        stock_text = response.css("p.instock.availability::text").getall()
        stock_str = "".join(stock_text).strip()
        # »звлекаем количество из строки вида "In stock (22 available)"
        import re
        stock_match = re.search(r"(\d+)", stock_str)
        amount_in_stock = int(stock_match.group(1)) if stock_match else 0

        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(response.css("div.product_main p.price_color::text").get().replace("?", "")),
            "amount_in_stock": amount_in_stock,
            "rating": rating_map.get(rating_str, 0),
            "category": response.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            "description": response.css("div#product_description ~ p::text").get("").strip(),
            "upc": response.css("table.table.table-striped tr:nth-child(1) td::text").get(),
        }

