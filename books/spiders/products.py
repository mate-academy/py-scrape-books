import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response, **kwargs):
        for book in response.css(".product_pod"):
            detail_page = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(response.urljoin(detail_page), callback=self.parse_detail_page)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_detail_page(response):
        title = response.css("h1::text").get()
        price = response.css(".price_color::text").get()
        amount_in_stock = "\n".join(response.css("p.availability::text").getall()).replace("\n", " ").strip().split()[2][1:]
        rating = response.css("p.star-rating::attr(class)").get().split()[-1]
        category = response.css(".breadcrumb a::text").getall()[-1]
        description = response.css(".sub-header + p::text").get()
        upc = response.css(".table-striped td::text").get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
