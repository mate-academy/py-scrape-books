import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get() or ""

        price_text = response.css("table tr:nth-child(4) td::text").get()
        price = float(price_text.replace("£", "")) if price_text else 0.0

        stock_text = response.css("table tr:nth-child(6) td::text").get()
        digits = "".join(
            [c for c in stock_text if c.isdigit()]
        ) if stock_text else ""
        amount_in_stock = int(digits) if digits else 0

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = rating_map.get(
            rating_class.split()[-1], 0
        ) if rating_class else 0

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get() or ""

        description = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).get()
        description = description.strip() if description else ""

        upc = response.css("table tr:nth-child(1) td::text").get() or ""

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
