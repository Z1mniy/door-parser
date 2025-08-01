import os
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

from assets.links_set import links_set_distributor
from assets.json_creator import create_JSON, add_to_JSON

IMG_BASE_PATH = './img/doors007'
PAGE_LOAD_WAIT = 1
CLICK_WAIT = 1

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)


def download_images(image_urls, door_name, site_name):
    photos_url = []
    for k, img_url in enumerate(image_urls, start=1):
        response = requests.get(img_url, stream=True)
        response.raise_for_status()

        file_extension = os.path.splitext(img_url)[1] or ".jpg"
        filename = os.path.join(IMG_BASE_PATH, door_name, f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, img_url])

    return photos_url


def parse_product_card(driver, site_name):
    name = driver.find_element(By.TAG_NAME, "h1").text
    price = driver.find_element(By.CLASS_NAME, "new").text
    door_url = driver.current_url

    features_list = []
    try:
        features_container = driver.find_element(By.CLASS_NAME, "prod_features")
        features = features_container.find_elements(By.CLASS_NAME, "item")

        for feature in features:
            key = feature.find_element(By.CLASS_NAME, 'name').text
            val = feature.find_element(By.CLASS_NAME, 'val').text
            features_list.append([key, val])
    except Exception:
        pass

    door_name = name.replace(" ", "_").replace("\"", "")
    ensure_directory(os.path.join(IMG_BASE_PATH, door_name))

    image_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'fancy_img')]")
    image_urls = [el.get_attribute('href') for el in image_elements]

    photos_url = download_images(image_urls, door_name, site_name)
    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)

    time.sleep(CLICK_WAIT)


def parser_007():
    site_url = "https://doors007.ru/"
    site_name = "doors007"

    ensure_directory(IMG_BASE_PATH)
    create_JSON(site_url, site_name)

    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for page_url in links:
        driver.get(page_url)
        time.sleep(PAGE_LOAD_WAIT)

        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "product_wrap")
            total_products = len(product_cards)

            for i in range(total_products):
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//div[contains(@class, 'name')]/a)[{i + 1}]"
                    ))
                )

                ActionChains(driver).move_to_element(product).click().perform()
                parse_product_card(driver, site_name)
                driver.back()
                time.sleep(CLICK_WAIT)

            try:
                next_button = driver.find_element(By.CLASS_NAME, "next")
                next_button.click()
                time.sleep(PAGE_LOAD_WAIT)
            except Exception:
                break

        driver.back()

    print("Процесс завершен")
