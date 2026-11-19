BOT_NAME = "scrape_books"

SPIDER_MODULES = ["scrape_books.spiders"]
NEWSPIDER_MODULE = "scrape_books.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.1

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,
    },
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
