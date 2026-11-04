BOT_NAME = "books"

SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True

FEEDS = {
    "books.jl": {"format": "jsonlines", "encoding": "utf8", "overwrite": True},
}
FEED_EXPORT_ENCODING = "utf-8"
