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

IMG_BASE_PATH = './img/forpost'
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
    price = driver.find_element(By.CLASS_NAME, "us-price-actual").text
    door_url = driver.current_url

    features_list = []
    try:
        container = driver.find_element(By.CLASS_NAME, "us-product-attributes-cont")
        features = container.find_elements(By.CLASS_NAME, "us-product-attr-item")
        for item in features:
            spans = item.find_elements(By.TAG_NAME, "span")
            if len(spans) == 1:
                features_list.append([spans[0].text, "none"])
            elif len(spans) >= 2:
                features_list.append([spans[0].text, spans[1].text])
    except Exception:
        features_list = [["none", "none"]]

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.CLASS_NAME, "additional-gallery-item")
    image_paths = [el.get_attribute('href') for el in image_elements]

    if not image_paths:
        try:
            fallback_image = driver.find_element(By.CLASS_NAME, 'oct-gallery')
            image_paths.append(fallback_image.get_attribute('href'))
        except Exception:
            pass

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_forpost():
    site_name = "forpost"
    web_site = "https://forpostroznica.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "product-grid")
            if not product_cards:
                break

            for i in range(len(product_cards)):
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//div[contains(@class, 'us-module-title')]/a)[{i + 1}]"
                    ))
                )
                try:
                    modal = driver.find_element(By.CLASS_NAME, "modal-close")
                    modal.click()
                except:
                    pass

                ActionChains(driver).move_to_element(product).click().perform()
                parse_product_card(driver, site_name)
                driver.back()

            try:
                pagination = driver.find_element(By.CLASS_NAME, 'pagination')
                buttons = pagination.find_elements(By.TAG_NAME, 'a')
                next_button = buttons[-2] if buttons[-2].text == '>' else None
                if next_button:
                    next_button.click()
                else:
                    break
            except Exception:
                break

        driver.back()

    print("Процесс завершен")
