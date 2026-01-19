import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get()

        price = response.css("p.price_color::text").get()

        stock_text = response.css("p.instock.availability::text").getall()
        amount_in_stock = "".join(stock_text).strip()

        rating_class = response.css("p.star-rating").attrib.get("class")
        rating = rating_class.replace("star-rating", "").strip()

        category = response.css("ul.breadcrumb li a::text").getall()[-1]

        description = response.css("#product_description ~ p::text").get()

        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
