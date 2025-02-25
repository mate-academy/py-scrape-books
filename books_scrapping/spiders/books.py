import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    all_urls = []
    # def get_rating(self, response):
    #   _map_rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    #   res = response.css(".star-rating::attr(class)").get().split()[-1]
    #   return _map_rating.get(res, 0)
        
        
    def parse(self, response, **kwargs):
      for book in response.css(".product_pod"):
        book_url = book.css(".image_container a::attr(href)").get()
        full_link = response.urljoin(book_url)
        yield response.follow(full_link, callback=self.parse_book)
        
      next_page = response.css("li.next a::attr(href)").get()
      if next_page is not None:
        yield response.follow(next_page, callback=self.parse)
        
    def parse_book(self, response):
      yield {
          "title": response.css(".product_main h1::text").get(),
          "price": response.css(".price_color::text").get(),
          "amount_in_stock": response.xpath("//td[contains(text(), 'In stock')]/text()").get(),
          "rating": response.css(".star-rating::attr(class)").get().split()[-1],
          "category": response.css(".breadcrumb li a::text").getall()[-1].strip(),
          "description": response.css(".product_page > p::text").get(),
          "upc": response.css(".table-striped").xpath("//td[1]/text()").get()          
        }
