# Books Scraper

This project uses Scrapy to parse books from [https://books.toscrape.com/](https://books.toscrape.com/). 
It navigates through all 50 pagination pages and extracts detailed information for all 1000 books.

## How to run the spider
From the root directory of the project, run:
```bash
scrapy crawl books
```

## Scraped fields:
- Title
- Price
- Amount in stock (defaults to 0 if not found)
- Rating (converted from text class to integer, defaults to None if not found)
- Category
- Description
- UPC

## How to run the spider
From the root directory of the project, run:
\`\`\`bash
scrapy crawl books
\`\`\`
Because `FEEDS` is configured in `settings.py`, this command will automatically generate (or overwrite) the `books.jl` file in JSON Lines format.

## Verification
The resulting `books.jl` file contains exactly 1000 lines, corresponding to the 1000 books available on the website.