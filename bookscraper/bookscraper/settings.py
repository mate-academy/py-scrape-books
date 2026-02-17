BOT_NAME = "bookscraper"

SPIDER_MODULES = ["bookscraper.spiders"]
NEWSPIDER_MODULE = "bookscraper.spiders"

ROBOTSTXT_OBEY = True

FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,
    }
}

# Configure item pipelines (uncomment if you decide to use pipelines later)
# ITEM_PIPELINES = {
#    "bookscraper.pipelines.BookScraperPipeline": 300,
# }