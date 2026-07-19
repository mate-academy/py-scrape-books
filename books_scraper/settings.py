# Scrapy settings for books_scraper project
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ROBOTSTXT_OBEY = True

# Be polite to the sandbox server: one request at a time, one second apart.
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "overwrite": True,
    },
}
