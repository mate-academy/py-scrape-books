BOT_NAME = "scrape_spider"

SPIDER_MODULES = ["scrape_spider.spiders"]
NEWSPIDER_MODULE = "scrape_spider.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 1

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    },
}
