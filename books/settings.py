# Scrapy settings for books project

BOT_NAME = "books"
SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True
LOG_LEVEL = "INFO"

# Коректний User-Agent
USER_AGENT = "Mozilla/5.0 (compatible; books-scraper/1.0)"

# Трохи повільніше, щоб бути «ввічливим»
DOWNLOAD_DELAY = 0.25

# Фід для збереження у books.jl (JSON Lines)
FEEDS = {
    "books.jl": {
        "format": "jsonlines",
        "encoding": "utf8",
        "overwrite": True,   # перезаписувати файл кожен запуск
        "indent": None,
    }
}

# Якщо використав BeautifulSoup для опису:
# встанови в середовищі: pip install beautifulsoup4
