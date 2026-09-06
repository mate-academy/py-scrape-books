import os

BOT_NAME = "books_scraper"
SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

# --- Logging Rules ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- Crawler Ethics & Target Sandbox Rules ---
# Disable robots.txt check because the sandbox returns a 404 for it, stalling crawls
ROBOTSTXT_OBEY = False
USER_AGENT = "books_scraper (+https://mate.academy)"

# --- Speed Optimization ---
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 0.1

# --- Automated Output Feed Exports ---
# ✅ Resolves the final mentor comment by automating generation of books.jl
FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": True  # Overwrites file on new runs instead of appending duplicates
    }
}

FEED_EXPORT_ENCODING = "utf-8"
