import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    def parse(self, response: Response, **kvargs):
        book_page_links = response.css('article h3 a::attr(href)')
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

    @staticmethod
    def parse_book(response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        def extract_with_css_list(query):
            return response.css(query).getall()

        yield {
            "title": extract_with_css("h1::text"),
            "price": float(extract_with_css(".price_color::text").replace("\u00a3", "")),
            "amount_in_stock": int(extract_with_css_list(".availability::text")[1].strip().split()[2][1:]),
            "rating": w2n.word_to_num(response.css("p.star-rating::attr(class)").get().split()[-1]),
            "category": extract_with_css_list(".breadcrumb li a::text")[2],
            "description": extract_with_css_list("p::text")[10],
            "upc": extract_with_css("td::text"),
        }