BOT_NAME = "book_scraper"

SPIDER_MODULES = ["book_scraper.spiders"]
NEWSPIDER_MODULE = "book_scraper.spiders"

ADDONS = {}

# books.toscrape.com is a training sandbox with no robots.txt, so we do
# not restrict crawling.
ROBOTSTXT_OBEY = False

# Crawl the sandbox concurrently but without hammering it
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 0

# Export every scraped book to books.jl, so a plain `scrapy crawl books`
# produces the required output file without extra flags.
FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True,
    },
}
