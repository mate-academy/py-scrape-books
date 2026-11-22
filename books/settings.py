BOT_NAME = "books"

SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.25

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "overwrite": True,
        "encoding": "utf-8",
    },
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
