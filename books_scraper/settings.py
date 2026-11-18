BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,
    },
}
