import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str):
        self.driver.quit()

    def parse(self, response, **kwargs):
        for book in response.css(".product_pod"):
            rating_word = book.css(".star-rating::attr(class)").re_first(r'star-rating\s+(\w+)')
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating_number = rating_map.get(rating_word, 0)

            title = book.css("h3 a::attr(title)").get()
            price = float(book.css(".price_color::text").get().replace("£", ""))

            book_url = response.urljoin(book.css("h3 a::attr(href)").get())
            additional_info = self._parse_additional_information(book_url)

            yield {
                "title": title,
                "price": price,
                "amount_in_stock": additional_info["amount_in_stock"],
                "rating": rating_number,
                "category": additional_info["category"],
                "description": additional_info["description"],
                "upc": additional_info["upc"],
            }

        next_page = response.css(".pager li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_additional_information(self, book_url):
        self.driver.get(book_url)

        amount_in_stock = self.driver.find_element(
            By.CSS_SELECTOR,
            ".instock.availability"
        ).text.replace("(", "").replace(")", "").split()[-2]

        category = self.driver.find_element(
            By.XPATH,
            "//ul[@class='breadcrumb']/li[3]/a"
        ).text

        description = self.driver.find_element(
            By.CSS_SELECTOR,
            "#product_description + p"
        ).text

        upc = self.driver.find_element(
            By.CSS_SELECTOR,
            ".table-striped tbody tr:nth-child(1) td:nth-child(2)"
        ).text

        return {
            "amount_in_stock": int(amount_in_stock),
            "category": category,
            "description": description,
            "upc": upc
        }
