from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By  # приватные методы
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from auth_data import user_name, password, headers
import os
import requests
import random
import csv
import json


"""
Здесь у меня смешан Selenium & requests, это бардак
-Аутентификация на сайте 
https://www.kuvalda.ru/
- ввод в поисковую строку слова Шуруповерт
-скролл
-сохранение страницы
-сбор наименования продукта, стоимости, старой цены, ссылки
-запись в CSV, JSON
"""

def authorization(user_name, password, headers):
    
    target = input("Привет, введи, что из инструментов тебя интересует: ")
    
    # запросы буду делать в одной ссесии
    sess = requests.Session()
    
    # переменная для записи в json
    all_json_data = []
    
    # переменная для записи в csv
    all_csv_data = []
    
    url = "https://www.kuvalda.ru/"
    
    # объект опций
    options = webdriver.ChromeOptions()    
    
    # вручную прописал user_agent (сделать список разных!!!, отключить обнаружение, сделать исполнение скрипта скрытое)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36")

    # инициализация драйвера (это обновленный селениум)
    s = Service(executable_path="/home/heyartem/PycharmProjects/Parsing_project/selenium_practice/web_driver/chromedriver")
    driver = webdriver.Chrome(service=s, options=options)
    
    time.sleep(2)
    
    try:
        driver.get(url=url)
        driver.maximize_window()
        time.sleep(3)
        
        # нахожу кнопку, что бы вызвать форму для ввода username & login.
        # скрипт сам определит, когда загрузятся все веб элементы, 
        # max.время ожидания 10 сек.
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header-top__login"))
        )        
       
        # кликаю кнопку
        login_button.click()
        
        #  ввожу маил (перед этим нахожу поле ввода и когда элемент загрузился)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='auth_1']")) # ищу по Тегу-"input", Атрибуту-"id"
        )
        email_input.clear()     # очищаю поле
        email_input.send_keys(user_name)
        
        # ввожу маил
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='auth_2']"))
        )
        password_input.clear()
        password_input.send_keys(password)
        
        # имитирую нажатие ENTER
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # нахожу строку "Поиск по каталогу" и ввожу "Шуруповерт"
        search_input = WebDriverWait(driver, 10).until(
            # EC.presence_of_element_located((By.CLASS_NAME, "//input[@class='search__input']"))
            EC.presence_of_element_located((By.CLASS_NAME, "search__input"))
        )
        search_input.clear()
        search_input.send_keys(target)
        search_input.send_keys(Keys.ENTER)
        time.sleep(5)        
        
        # скролл 1
        driver.execute_script("window.scrollTo(0, 2000)")        
        time.sleep(3)
        
        # скролл 2
        driver.execute_script("window.scrollTo(2000, 6000)")        
        time.sleep(3)   
        
        # скролл до нижней части страницы
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(2)
        
        # создал директорию для сохранения
        if not os.path.exists("data2"):
            os.mkdir("data2")
        
        # сохраняю страницу
        with open("data2/data_selenium.html", "w") as file:
            file.write(driver.page_source)
        
    # блок, если будет ошибка
    except Exception as ex:
        print(ex)
    
    finally:    
        driver.close()    
        driver.quit()
        
    with open ("data2/data_selenium.html") as file:
        src = file.read()
    
    soup = BeautifulSoup(src, "lxml")
    
    # пагинация, страниц может быть одна! поэтому в except "last_page = int(1)"
    try:
        last_page = int(soup.find("div", class_="catalog__footer").find("div", class_="pagination").find_all("a", class_="pagination__item")[-1].text)
    except Exception as ex:
        last_page = int(1)
        
    # инфоблок
    print(f"[info] found {last_page} pages\n")
    
    for page in range(1, last_page + 1)[:1]:
        # url_page = (f"https://www.kuvalda.ru/catalog/7309-shurupoverty/page-{page}/")
        url_page = (f"https://www.kuvalda.ru/catalog/search/page-{page}/?keyword={target}/")
        
        # инфоблок
        print(f"[info]  working with the page\n{url_page}\n")
        
        # пауза между запросами
        time.sleep(random.randrange(2, 4))
        
        # запрос к каждой странице
        response = sess.get(url=url_page, headers=headers)
        
        # with open("data2/dataaaaa.html", "w") as file:
        #     file.write(response.text)
        
        soup = BeautifulSoup(response.text, "lxml")
    
        # общий блок с каротчками
        # block_cards = soup.find("div", id="catalog-list").find_all("div", class_="snippet_mounted")
        block_cards = soup.find("div", id="catalog-list").find_all("div", class_="catalog__list-item")
        
        # инфоблок
        print(f"[info] found block_cards\n")
        print(block_cards)
        
        for i in block_cards:
            
            """ В ЭТОТ ЦИКЛ НЕ ВХОДИТ! Почему???"""
            # инфоблок
            print(f"[info]  entered the cucle\n")
            
            # наименование продукта
            try:
                card_brend_dirty = i.find("a", class_="snippet__title").text
                card_brend = " ".join(card_brend_dirty.split())
            except Exception as ex:
                card_brend = "No data card_brend"
            
            # прайс
            try:
                card_price = i.find("span", class_="snippet__price-value").text.replace(" ", "")
            except Exception as ex:
                card_price = "No data card_price"
            
            # старый прайс
            try:
                card_old_price = i.find("s", class_="snippet__price-old").text.replace(" ", "")
            except Exception as ex:
                card_old_price = "No old price"
            
            # ссылка на продукт
            try:
                card_link = f'https://www.kuvalda.ru{i.find("div", class_="snippet__photo").find("a").get("href")}'
            except Exception as ex:
                card_link = "No data card_link"            
            
            print(f"Brend: {card_brend}\nPrice: {card_price}\nOld-price: {card_old_price}\nLink: {card_link}\n{10 * '- -'}")            
            
    #         # упаковываю дянные для записи в json
    #         all_json_data.append(
    #             {
    #                 "card_brend": card_brend,
    #                 "card_price": card_price,
    #                 "card_old_price": card_old_price,
    #                 "card_link": card_link
    #             }
    #         )
            
    #         # упаковываю данные для записи в csv
    #         all_csv_data.append(
    #             [
    #                 card_brend,
    #                 card_price,
    #                 card_old_price,
    #                 card_link
    #             ]
    #         )
            
    #     # инфоблок
    #     print(f"[info] completed page {page} of {last_page}")
            
    # # записываю csv
    # with open("data2/data_product.csv", "w") as file:
    #     writer = csv.writer(file)   # создал писателя
    #     writer.writerow(        # записываю заголовки
    #         (
    #             "Name_product",
    #             "Price",
    #             "Old_Price",
    #             "Link"
    #         )
    #     )
    #     writer.writerows(all_csv_data)      # записываю значения
        
    # # записываю json
    # with open("data2/data_json_product.json", 'w') as file:
    #     json.dump(all_json_data, file, indent=4, ensure_ascii=False)
        
    # # инфоблок
    # print(f"\n[info] data collection completed!")
    

def main():
    authorization(user_name, password, headers)
    

if __name__ == "__main__":
    main()
