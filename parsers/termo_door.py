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


IMG_BASE_PATH = './img/termo-door'
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
    price = driver.find_element(By.CLASS_NAME, "price").text
    door_url = driver.current_url

    features_container = driver.find_elements(By.TAG_NAME, "dl")[1]
    feature_names = features_container.find_elements(By.TAG_NAME, "dt")
    feature_values = features_container.find_elements(By.TAG_NAME, "dd")

    features_list = [
        [feature_names[i].text, feature_values[i].text]
        for i in range(len(feature_names))
    ]

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'push-to-fancybox')]/a")
    image_paths = [el.get_attribute('href') for el in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_termo_door():
    site_name = "termo-door"
    web_site = "https://termo-door.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "one-product")
            if not product_cards:
                break
            card_height = product_cards[0].size['height']

            for i in range(len(product_cards)):
                time.sleep(CLICK_WAIT)
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//div[contains(@class, 'image-block')])[{i + 1}]"
                    ))
                )
                product.click()
                parse_product_card(driver, site_name)
                driver.back()

            buttons = driver.find_elements(By.CLASS_NAME, 'inline-link')
            if not buttons or (len(buttons) < 2 and buttons[0].text != '→'):
                break

            driver.execute_script(f'window.scrollBy(0, {card_height});')
            (buttons[0] if len(buttons) == 1 else buttons[1]).click()

        driver.back()

    print("Процесс завершен")


