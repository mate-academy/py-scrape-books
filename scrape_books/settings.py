BOT_NAME = "scrape_books"

SPIDER_MODULES = ["scrape_books.spiders"]
NEWSPIDER_MODULE = "scrape_books.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = False
CLOSESPIDER_ITEMCOUNT = 1000

CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 0

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "store_empty": False,
        "indent": 4,
    },
}
