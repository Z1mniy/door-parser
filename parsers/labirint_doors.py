import os
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from assets.links_set import links_set_distributor
from assets.json_creator import create_JSON, add_to_JSON

from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

IMG_BASE_PATH = './img/labirint_doors'
PAGE_LOAD_WAIT = 4
CLICK_WAIT = 1
SCROLL_WAIT = 1


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


def download_images(image_paths, current_door, web_site):
    photos_url = []
    for k, img in enumerate(image_paths, start=1):
        link_to_img = web_site.rstrip('/') + img
        response = requests.get(link_to_img, stream=True)
        response.raise_for_status()

        file_extension = os.path.splitext(img)[1] or ".jpg"
        filename = os.path.join(f'{IMG_BASE_PATH}/{current_door}', f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, link_to_img])

    return photos_url


def parse_product_card(driver, web_site):
    name = driver.find_element(By.TAG_NAME, "h1").text
    time.sleep(.5)
    price = driver.find_element(By.CLASS_NAME, "product-01__current-price").text
    door_url = driver.current_url

    features = driver.find_elements(By.CLASS_NAME, "product-01__parameters-item")
    features_list = [
        [
            item.find_element(By.TAG_NAME, "dt").text,
            item.find_element(By.TAG_NAME, "dd").text
        ]
        for item in features
    ]

    current_door = name.replace(" ", "_")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    images_path_raw = driver.find_element(
        By.CLASS_NAME, "product-gallery-01__stage-item-img-container"
    ).get_attribute("items")

    data = json.loads(images_path_raw)
    image_paths = [item['src'] for item in data]

    photos_url = download_images(image_paths, current_door, web_site)

    add_to_JSON(name, price, features_list, photos_url, door_url, "labirint")
    time.sleep(CLICK_WAIT)


def parser_labirint_doors():
    ensure_directory(IMG_BASE_PATH)
    web_site = "https://labirintdoors.ru/"
    site_name = "labirint"

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        outside_counter = 0
        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "products-list-01-item__header")
            count_of_products = len(product_cards) - outside_counter

            for i in range(outside_counter, outside_counter + count_of_products):
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//div[contains(@class, 'products-list-01-item__content_btn-level')])[{i + 1}]"
                    ))
                )
                product.click()
                parse_product_card(driver, web_site)
                driver.back()

            try:
                button = driver.find_element(By.CLASS_NAME, "products-lazy-pagination_position_after")
                button.click()
                time.sleep(SCROLL_WAIT)
                outside_counter = i + 1
            except Exception:
                break

        driver.back()

    print("Процесс завершен")
