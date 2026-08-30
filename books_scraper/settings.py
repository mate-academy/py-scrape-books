"""Settings for the books scraper."""

BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0.1
LOG_LEVEL = "INFO"

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    }
}
