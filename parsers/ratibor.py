import os
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

from assets.links_set import links_set_distributor
from assets.json_creator import create_JSON, add_to_JSON

IMG_BASE_PATH = './img/ratibor'
PAGE_LOAD_WAIT = 2
CLICK_WAIT = 1.5
SCROLL_DIVIDER = 3

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)

def download_images(image_paths, current_door):
    photos_url = []
    for k, img in enumerate(image_paths, start=1):
        response = requests.get(img, stream=True)
        response.raise_for_status()

        file_extension = os.path.splitext(img)[1] or ".jpg"
        filename = os.path.join(f'{IMG_BASE_PATH}/{current_door}', f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, img])

    return photos_url

def parse_product_card(driver, site_name):
    name = driver.find_element(By.TAG_NAME, "h1").text
    price = driver.find_element(By.XPATH, "//div[@class='price-current']/strong").text
    door_url = driver.current_url

    features_container = driver.find_element(By.CLASS_NAME, "product-options")
    features = features_container.find_elements(By.TAG_NAME, "li")
    features_list = []

    counter = 0
    for row in features:
        if counter != 0:
            feature_name = row.find_element(By.CLASS_NAME, "option-title")
        else:
            feature_name = row.find_element(By.TAG_NAME, "a")
            counter = 1

        try:
            feature_description = row.find_element(By.CLASS_NAME, "option-body").text
        except Exception:
            feature_description = "none"

        features_list.append([feature_name.text, feature_description])

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'slick-slide')]/a")
    image_paths = [el.get_attribute('href') for el in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_ratibor():
    site_name = "ratibor"
    web_site = "https://dveri-ratibor.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        product_cards = driver.find_elements(By.CLASS_NAME, "shop2-product-item")
        count_of_products = len(product_cards)
        card_height = product_cards[0].size['height']

        for i in range(count_of_products):
            time.sleep(CLICK_WAIT)
            product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"(//div[contains(@class, 'product-top')])[{i + 1}]"
                ))
            )
            product.click()
            parse_product_card(driver, site_name)
            driver.back()
            driver.execute_script(f'window.scrollBy(0, {card_height // SCROLL_DIVIDER});')

        driver.back()

    print("Процесс завершен")
