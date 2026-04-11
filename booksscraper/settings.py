BOT_NAME = "booksscraper"

SPIDER_MODULES = ["booksscraper.spiders"]
NEWSPIDER_MODULE = "booksscraper.spiders"

# Be polite
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = True

# Output
FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "overwrite": True,
    }
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
