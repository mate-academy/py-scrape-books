
BOT_NAME = "books"

SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 0.5

CONCURRENT_REQUESTS_PER_DOMAIN = 8

FEED_EXPORT_ENCODING = "utf-8"

USER_AGENT = (
    "Mozilla/5.0 (compatible; BooksScraper/1.0)"
)

LOG_LEVEL = "INFO"
