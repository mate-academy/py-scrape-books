import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response: scrapy.http.Response) -> scrapy.http.Response:
        book_page_links = response.css("div.image_container a::attr(href)")
        yield from response.follow_all(book_page_links, self.parse_book)

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: scrapy.http.Response) -> dict:
        rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get()[1:],
            "amount_in_stock": response.css("p.instock.availability").re_first(r"\((.*?)\)").split()[0],
            "rating": rating_dict.get(response.css("p.star-rating::attr(class)").get().split()[1], 0),
            "category": response.css("ul.breadcrumb > li > a::text").getall()[-1],
            "description": response.css("article.product_page > p::text").get(),
            "upc": response.css("table.table-striped > tr > td::text").get(),
        }
