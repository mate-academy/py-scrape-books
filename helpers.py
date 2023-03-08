from dataclasses import dataclass, field

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


@dataclass
class Book:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str


def get_stock_amount(string: str) -> int:
    return int("".join([num for num in string if num.isnumeric()]))


def get_rating(driver: WebDriver) -> int:
    help_dict = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return help_dict[driver.find_element(By.CLASS_NAME, "star-rating").get_attribute("class").split()[1]]


def parse_page(driver: WebDriver) -> Book:
    title = driver.find_element(By.CSS_SELECTOR, "h1").text
    price = float(driver.find_element(By.CLASS_NAME, "price_color").text.replace("£", ""))
    amount_in_stock = get_stock_amount(driver.find_element(By.CLASS_NAME, "availability").text)
    rating = get_rating(driver)
    category = driver.find_elements(By.CSS_SELECTOR, ".breadcrumb > li")[2].text
    try:
        description = driver.find_element(By.CSS_SELECTOR, "article.product_page > p").text
    except NoSuchElementException:
        description = "Not provided on the site"
    upc = driver.find_element(By.CSS_SELECTOR, "tr > td").text

    return Book(
        title=title,
        price=price,
        amount_in_stock=amount_in_stock,
        rating=rating,
        category=category,
        description=description,
        upc=upc
    )
