from __future__ import annotations

BOT_NAME = "bookscraper"

SPIDER_MODULES = ["bookscraper.spiders"]
NEWSPIDER_MODULE = "bookscraper.spiders"

ROBOTSTXT_OBEY = True

# Keep concurrency modest; site is a demo, but let's be polite.
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.1

# Ensure deterministic output to books.jl at project root.
FEEDS = {
    "books.jl": {
        "format": "jl",
        "encoding": "utf8",
        "overwrite": True,
        "indent": None,  # compact lines
    }
}

FEED_EXPORT_ENCODING = "utf-8"
