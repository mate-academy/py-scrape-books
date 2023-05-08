import scrapy
from word2number import w2n


class BookSpiderSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response, *args, **kwargs):
        total_pages = int(response.css(
            ".pager .current::text"
        ).get().strip().split()[-1])

        url_pages = [
            f"https://books.toscrape.com/catalogue/page-{n}.html"
            for n in range(1, total_pages + 1)
        ]

        for url in url_pages:
            yield scrapy.Request(
                url,
                callback=self.parse_links_to_detail_page
            )

    def parse_links_to_detail_page(self, response):
        detail_book_links = response.css(
            ".product_pod h3 a::attr(href)"
        ).getall()

        for link in detail_book_links:
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_book_info
            )

    @staticmethod
    def get_rating(product):

        rating_str = product.css(
            ".product_pod .star-rating"
        ).attrib["class"].split()[-1]

        return w2n.word_to_num(rating_str)

    def parse_book_info(self, response):
        product = response.css(".product_page")[0]

        title = product.css("h1::text").get()
        price = product.css(".price_color::text").get().replace("£", "")
        description = product.css("#product_description + *::text").get()
        category = response.css('ul.breadcrumb li a::text')[-1].get().strip()
        upc = product.css(".table td::text").get()
        rating = self.get_rating(product)
        amount_in_stock = int(
            product.css(".table td::text")[-2]
            .get().split("(")[-1].split()[0]
        )

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
