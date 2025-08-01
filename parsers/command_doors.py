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


IMG_BASE_PATH = './img/cmdoors'
PAGE_LOAD_WAIT = 2
CLICK_WAIT = 1.5
SCROLL_STEP = 200


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

        file_extension = ".jpg"
        filename = os.path.join(f'{IMG_BASE_PATH}/{current_door}', f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, img])

    return photos_url

def parse_product_card(driver, site_name):
    name = driver.find_element(By.CLASS_NAME, "doorname").text
    price = driver.find_element(By.ID, "totalprice").text
    door_url = driver.current_url

    features_container = driver.find_element(By.CLASS_NAME, "chars_list")
    features = features_container.find_elements(By.TAG_NAME, "li")
    features_list = []
    for item in features:
        text = item.text
        if ":" in text:
            k = text.find(":")
            features_list.append([text[:k], text[k + 1:].strip()])

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.CLASS_NAME, "panel_back__item")
    front_door_img = driver.find_element(By.CLASS_NAME, 'front_door_img')
    image_elements.append(front_door_img)

    ActionChains(driver).move_to_element(image_elements[0]).perform()
    time.sleep(5)

    image_paths = []
    for el in image_elements:
        src = el.get_attribute('src')
        if src:
            image_paths.append(src)
            driver.execute_script(f'window.scrollBy(0, {SCROLL_STEP});')
            time.sleep(0.2)

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_command_doors():
    site_name = "cmdoors"
    web_site = "https://cmdoors.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        product_cards = driver.find_elements(By.CLASS_NAME, "product")
        count_of_products = len(product_cards)

        for i in range(count_of_products):
            time.sleep(CLICK_WAIT)
            product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"(//div[contains(@class, 'product__hover')])[{i + 1}]"
                ))
            )
            product.click()
            time.sleep(0.5)  # возможно требуется двойной клик
            product.click()
            parse_product_card(driver, site_name)
            driver.back()

        driver.back()

    print("Процесс завершен")
