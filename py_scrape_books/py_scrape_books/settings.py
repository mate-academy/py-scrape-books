BOT_NAME = "py_scrape_books"

SPIDER_MODULES = ["py_scrape_books.spiders"]
NEWSPIDER_MODULE = "py_scrape_books.spiders"

ROBOTSTXT_OBEY = True

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jl",
        "encoding": "utf8",
        "store_empty": False,
        "fields": ["title", "price", "amount_in_stock", "rating", "category", "description", "upc"],
        "indent": None,
    },
}

DOWNLOAD_DELAY = 0.5
