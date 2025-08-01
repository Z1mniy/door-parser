
# import os
# import requests
# import json
# import time 

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# from assets.links_set import links_set_distributor
# from assets.json_creator import create_JSON, add_to_JSON

# def product_card_parsing(driver, web_site):
            
#     name = driver.find_element(By.TAG_NAME, "h1").text
#     price = driver.find_element(By.TAG_NAME, "bdi").text
#     door_url = driver.current_url
    
#     feauters_container = driver.find_element(By.XPATH, "//div[contains(@class, 'woocommerce-product-details__short-description')]/p")
#     feauters = feauters_container.find_elements(By.TAG_NAME, "strong")
#     # feauters_descriptions = feauters_container.find_elements(By.TAG_NAME, "dd")
#     # print(len(feauters))
#     feauters_list = []
#     for j in range(len(feauters)):
#         i = feauters[j].text.find(":")
#         feauters_list.append([feauters[j].text[:i],feauters[j].text[i:]])


#     current_door = name.replace(" ", "_").replace("\"", "")
#     os.makedirs(f'./img/{web_site}/{current_door}', exist_ok=True)

#     # images_galery = driver.find_element(By.CLASS_NAME, "polite")
#     image_paths = driver.find_elements(By.XPATH, "//div[contains(@class, 'woocommerce-product-gallery__image')]/a")
#     image_paths_list = []
#     for i in image_paths:
#         image_paths_list.append(i.get_attribute('href'))
#     k=0

#     time.sleep(2)
#     photos_url = []
#     for img in image_paths_list:
#         k+=1
#         # driver.implicitly_wait(10)
#         link_to_img = img

#         # print(link_to_img)
#         response = requests.get(link_to_img, stream=True)
#         response.raise_for_status()  
        
#         # file_extension = os.path.splitext(link_to_img)[1]
#         # if not file_extension:
#         file_extension = ".jpg" 

#         filename = f'./img/{web_site}/{current_door}/image_{k}{file_extension}'
#         with open(filename, 'wb') as img_file:
#             img_file.write(response.content)
        
#         photos_url.append([filename, link_to_img])

#     add_to_JSON(name, price, feauters_list, photos_url, door_url, web_site)
        
#     time.sleep(1.5)


# def parser_mxd():
#     counter=0
#     web_site = "https://mxdoors.ru/"
#     site_name = "mxdoors"
#     os.makedirs(f'./img/{site_name}', exist_ok=True)

#     create_JSON(web_site, site_name)

#     links = links_set_distributor(site_name)
#     driver = webdriver.Chrome()

#     for current_link in links :
#         driver.get(current_link)
#         time.sleep(2)
        
#         outside_counter = 0
        
#         product_cards = driver.find_elements(By.CLASS_NAME,"nm-shop-loop-product-wrap")
#         count_of_products = len(product_cards)
#         # card_size = product_cards[0].size
#         # card_height = card_size['height']
#         # y = 0
#         for i in range(outside_counter, count_of_products):
#             time.sleep(1.5)
#             product = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, f"(//a[contains(@class, 'nm-shop-loop-title-link')])[{i+1}]"))
#             )
#             # driver.execute_script("arguments[0].click();", product)
#             # webdriver.ActionChains(driver).move_to_element(product ).click(product ).perform()
#             product.click()
#             product_card_parsing(driver, site_name)
#             driver.back()
#             # y+=card_height//2
#             # driver.execute_script(f'window.scrollBy(0, {card_height//3});')
            
                       
#         driver.back()

#     print("Процесс завершен")
#     return




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

IMG_BASE_PATH = './img/mxdoors'
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

        file_extension = ".jpg"  # MXD всегда jpg
        filename = os.path.join(f'{IMG_BASE_PATH}/{current_door}', f"image_{k}{file_extension}")

        with open(filename, 'wb') as img_file:
            img_file.write(response.content)

        photos_url.append([filename, img])

    return photos_url

def parse_product_card(driver, site_name):
    name = driver.find_element(By.TAG_NAME, "h1").text
    price = driver.find_element(By.TAG_NAME, "bdi").text
    door_url = driver.current_url

    features_list = []
    try:
        features_container = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'woocommerce-product-details__short-description')]/p"
        )
        features = features_container.find_elements(By.TAG_NAME, "strong")

        for f in features:
            text = f.text.strip()
            if ":" in text:
                k = text.index(":")
                features_list.append([text[:k], text[k + 1:].strip()])
    except Exception:
        pass

    current_door = name.replace(" ", "_").replace("\"", "")
    ensure_directory(f'{IMG_BASE_PATH}/{current_door}')

    image_elements = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'woocommerce-product-gallery__image')]/a"
    )
    image_paths = [el.get_attribute('href') for el in image_elements]

    photos_url = download_images(image_paths, current_door)

    add_to_JSON(name, price, features_list, photos_url, door_url, site_name)
    time.sleep(CLICK_WAIT)

def parser_mxd():
    site_name = "mxdoors"
    web_site = "https://mxdoors.ru/"
    ensure_directory(IMG_BASE_PATH)

    create_JSON(web_site, site_name)
    links = links_set_distributor(site_name)
    driver = webdriver.Chrome(options=options)

    for current_link in links:
        driver.get(current_link)
        time.sleep(PAGE_LOAD_WAIT)

        product_cards = driver.find_elements(By.CLASS_NAME, "nm-shop-loop-product-wrap")
        count_of_products = len(product_cards)

        for i in range(count_of_products):
            time.sleep(CLICK_WAIT)
            product = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"(//a[contains(@class, 'nm-shop-loop-title-link')])[{i + 1}]"
                ))
            )
            product.click()
            parse_product_card(driver, site_name)
            driver.back()

        driver.back()

    print("Процесс завершен")