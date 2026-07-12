BOT_NAME = "booksscraper"

SPIDER_MODULES = ["booksscraper.spiders"]
NEWSPIDER_MODULE = "booksscraper.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 0.25

DOWNLOAD_TIMEOUT = 30

RETRY_TIMES = 5

COOKIES_ENABLED = False

FEEDS = {
    "books.jl": {"format": "jsonlines", "overwrite": True},
}

ITEM_PIPELINES = {
}
