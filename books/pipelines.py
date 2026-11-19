from books.items import BooksItem


class BooksPipeline:
    def process_item(self, item: BooksItem, spider: object) -> BooksItem:
        return item
