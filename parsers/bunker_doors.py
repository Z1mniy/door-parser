import os
import json
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


from assets.links_set import links_set_distributor
from assets.json_creator import create_JSON, add_to_JSON

from selenium.webdriver.chrome.options import Options


IMG_BASE_PATH = './img/bunker_doors'
PAGE_LOAD_WAIT = 2
CLICK_WAIT = 1.5
SCROLL_WAIT = 2.0


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)

def download_images(image_paths, current_door):
    photos_url = []
    for k, img in enumerate(image_paths, start=1):
        link_to_img = img
        response = requests.get(link_to_img, stream=True)
        response.raise_for_status()

        file_extension = os.path.splitext(link_to_img)[1] or ".jpg"
        filename = os.path.join(f'{IMG_BASE_PATH}/{current_door}', f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, link_to_img])

    return photos_url

def parse_product_card(driver, site_name):
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

    images_gallery = driver.find_element(By.CLASS_NAME, "product-gallery-04")
    image_elements = images_gallery.find_elements(By.CLASS_NAME, "product-gallery-04__stage-item-img-container")
    image_paths = [img.get_attribute('href') for img in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_bunker_doors():
    site_name = "bunker"
    web_site = "https://bunkerdoors.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)
    action = ActionChains(driver)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        outside_counter = 0
        while True:
            product_cards = driver.find_elements(By.CLASS_NAME, "products-list-01-item__img")
            print(len(product_cards))
            count_of_products = len(product_cards) - outside_counter


            for i in range(outside_counter, count_of_products):
                time.sleep(CLICK_WAIT)
                try:
                    product = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            f"(//a[contains(@class, 'products-list-01-item__img-wrapper')])[{i + 1}]"
                        ))
                    )
                except TimeoutError:
                    break
                action.move_to_element(product).click().perform()
                parse_product_card(driver, site_name)
                driver.back()

            
            try:
                driver.execute_script("window.scrollBy(0,1000)")
                WebDriverWait(driver,10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='main-body']/div[2]/main/div/div/div[4]/div/div/div[2]/div/div/button"))
                ).click()
                time.sleep(SCROLL_WAIT)
                outside_counter = i + 1
            except:
                break

        driver.back()

    print("Процесс завершен")