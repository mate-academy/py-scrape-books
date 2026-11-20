BOT_NAME = "books"

SPIDER_MODULES = ["books_scraping.spiders"]
NEWSPIDER_MODULE = "books_scraping.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS_PER_DOMAIN = 8

DOWNLOADER_MIDDLEWARE_RESPONSE_EXCEPTIONS = True

FEED_EXPORT_ENCODING = "utf-8"
FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "mode": "overwrite",
    },
}
