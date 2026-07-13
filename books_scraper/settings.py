BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0.1
LOG_LEVEL = "INFO"

TELNETCONSOLE_ENABLED = False

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    },
}
