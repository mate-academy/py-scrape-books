from typing import List
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def scrap_pagination_urls(home_url: str) -> List[str]:
    options = Options()
    options.add_argument("--headless=new")
    try:
        driver = webdriver.Firefox(options=options)
        driver.get(home_url)
        urls = []
        next_link = driver.find_element(By.CLASS_NAME, "next")

        while True:
            next_link = next_link.find_element(By.TAG_NAME, "a")
            next_href = next_link.get_attribute("href")
            urls.append(urljoin(home_url, next_href))

            wait = WebDriverWait(driver, 2)
            wait.until(ec.presence_of_element_located((By.CLASS_NAME, "next")))

            next_link.click()

            next_link = driver.find_element(By.CLASS_NAME, "next")
    finally:
        driver.close()
        return urls

# if __name__ == "__main__":
#     scrap_pagination_urls("https://books.toscrape.com")
