from scrapy.http import Response


class BookScraper:
    def __init__(self, response: Response) -> None:
        self.response = response

    def get_book_dict(self) -> dict:
        return dict(
            title=self.get_title(),
            price=self.get_price(),
            amount_in_stock=self.get_amount_in_stock(),
            rating=self.get_rating(),
            category=self.get_category(),
            description=self.get_description(),
            upc=self.get_upc()
        )

    def get_title(self) -> str:
        item = self.response.css(".product_main > h1::text").get()
        return item

    def get_price(self) -> float:
        item = self.response.css(".price_color::text").get()
        return float(item[2:])

    def get_amount_in_stock(self) -> int:
        item = self.response.css("tr:nth-child(6) > td::text").extract_first()
        amount_in_stock = item.split()[2][1:]
        return int(amount_in_stock) if amount_in_stock is not None else 0

    def get_rating(self) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        item = self.response.css(".star-rating::attr(class)").get()
        return int(rating_map[item.split()[-1]])

    def get_category(self) -> str:
        item = self.response.css(".breadcrumb > li:nth-child(3) > a::text").get()
        return item

    def get_description(self) -> str:
        item = self.response.css("#content_inner > article > p::text").get()
        return item

    def get_upc(self) -> str:
        item = self.response.css("tr:nth-child(1) > td::text").extract_first()
        return item
