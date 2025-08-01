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

IMG_BASE_PATH = './img/STR'
PAGE_LOAD_WAIT = 2
CLICK_WAIT = 1.5

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
    price = driver.find_element(By.CLASS_NAME, "product__price-text").text
    door_url = driver.current_url

    # Переход на вкладку характеристик
    tabs = driver.find_elements(By.CLASS_NAME, "information__tab")
    if len(tabs) > 1:
        ActionChains(driver).move_to_element(tabs[1]).click().perform()
        time.sleep(0.5)

    features_list = []
    features_containers = driver.find_elements(By.CLASS_NAME, "features__list")
    for container in features_containers:
        items = container.find_elements(By.CLASS_NAME, 'features__item')
        for item in items:
            texts = item.find_elements(By.TAG_NAME, "p")
            if len(texts) == 1:
                features_list.append([texts[0].text, "none"])
            elif len(texts) >= 2:
                features_list.append([texts[0].text, texts[1].text])

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.XPATH, "//img[contains(@class, 'product__gallery-image')]")
    image_paths = [el.get_attribute('src') for el in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_str():
    site_name = "STR"
    web_site = "https://str12.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "product-card")
            if not product_cards:
                break

            for i in range(len(product_cards)):
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//article[contains(@class, 'product-card')]/a)[{i + 1}]"
                    ))
                )
                ActionChains(driver).move_to_element(product).click().perform()
                parse_product_card(driver, site_name)
                driver.back()

            try:
                button = driver.find_elements(By.CLASS_NAME, "next")
                driver.get(button[0].get_attribute('href'))
            except Exception:
                break

        driver.back()

    print("Процесс завершен")
