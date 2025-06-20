import scrapy

from scrape_book.items import Book


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    STAR_RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response, **kwargs):
        for book_article in response.css("article.product_pod"):
            detail_page_relative_url = book_article.css("h3 a::attr(href)").get()

            if detail_page_relative_url:
                price_text = book_article.css("p.price_color::text").get()
                star_rating_class = book_article.css("p.star-rating::attr(class)").get()
                book_title = book_article.css(
                    "h3 a::attr(title)").get()

                yield response.follow(
                    detail_page_relative_url,
                    callback=self.parse_book_details,
                    cb_kwargs={
                        'listing_price': price_text,
                        'listing_rating_class': star_rating_class,
                        'listing_title': book_title
                    }
                )

        next_page_relative_url = response.css("li.next a::attr(href)").get()

        if next_page_relative_url is not None:
            yield response.follow(next_page_relative_url, callback=self.parse)

    def parse_book_details(self, response, listing_price, listing_rating_class, listing_title):
        book_item = {'title': response.css("div.product_main h1::text").get().strip()}
        price_raw = response.css("p.price_color::text").get()
        book_item['price'] = float(price_raw.replace('£', ''))

        stock_text_raw = response.css("p.instock.availability::text").getall()
        stock_match = response.xpath('//p[@class="instock availability"]/text()').re_first(r'(\d+)\s+available')
        if stock_match:
            book_item['amount_in_stock'] = int(stock_match)
        else:
            book_item['amount_in_stock'] = 0

        rating_class = response.css("p.star-rating::attr(class)").get()
        if rating_class and "star-rating" in rating_class:
            rating_text = rating_class.split()[-1]
            book_item['rating'] = self.STAR_RATING_MAP.get(rating_text, 0)
        else:
            book_item['rating'] = 0

        book_item['category'] = response.css("ul.breadcrumb li:nth-child(3) a::text").get().strip()
        description_text = response.css("div#product_description + p::text").get()
        if description_text:
            book_item['description'] = description_text.strip()
        else:
            book_item['description'] = ""

        book_item['upc'] = response.css("table.table.table-striped tr:nth-child(1) td::text").get().strip()

        yield Book(
            title=book_item['title'],
            price=book_item['price'],
            amount_in_stock=book_item['amount_in_stock'],
            rating=book_item['rating'],
            category=book_item['category'],
            description=book_item['description'],
            upc=book_item['upc'],
        )
