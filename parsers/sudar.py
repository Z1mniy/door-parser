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

IMG_BASE_PATH = './img/sudar'
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
        if not img:
            continue

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

    features_list = []
    table = driver.find_element(By.TAG_NAME, "tbody")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 1:
            features_list.append([cells[0].text, "none"])
        elif len(cells) >= 2:
            features_list.append([cells[0].text, cells[1].text])

    current_door = name.replace(" ", "_").replace("\"", "").replace("/", "-")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'slick-slide')]/a")
    image_paths = []
    if len(image_elements) <= 1:
        try:
            fallback_img = driver.find_element(By.CLASS_NAME, 'venobox')
            image_paths.append(fallback_img.get_attribute('href'))
        except Exception:
            pass
    else:
        image_paths = [el.get_attribute('data-href') for el in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_sudar():
    site_name = "sudar"
    web_site = "https://closedoor.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "product ")
            if not product_cards:
                break
            card_height = product_cards[0].size['height']

            for i in range(len(product_cards)):
                product = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f"(//a[contains(@class, 'woocommerce-LoopProduct-link')])[{i + 1}]"
                    ))
                )
                ActionChains(driver).move_to_element(product).click().perform()
                parse_product_card(driver, site_name)
                driver.back()

            try:
                next_buttons = driver.find_elements(By.CLASS_NAME, "next")
                next_link = next_buttons[0].get_attribute('href')
                driver.get(next_link)
            except Exception:
                break

        driver.back()

    print("Процесс завершен")