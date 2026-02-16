BOT_NAME = "books"
SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True
LOG_LEVEL = "INFO"

USER_AGENT = "Mozilla/5.0 (compatible; books-scraper/1.0)"

DOWNLOAD_DELAY = 0.25

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,
        "indent": None,
    }
}

