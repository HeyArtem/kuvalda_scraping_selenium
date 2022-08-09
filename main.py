from selenium import webdriver
from auth_data import user_name, password
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service # при инициализации
import pickle
import time
import os
from bs4 import BeautifulSoup
import csv
import json

"""
Скрапинг  https://www.kuvalda.ru/ только с Selenium
-Аутентификация на сайте
-Сохранение cookies (в дальнейшем, при работе в фоновом режиме Hedless, отключить ввод регистрационных данных)
- ввод в поисковую строку любого слова от пользователя
-скролл
-сохранение страницы
-сбор наименования продукта, стоимости, старой цены, ссылки
-запись в CSV, JSON
"""


def initialization_driver():
    
    # объект опций
    options = webdriver.ChromeOptions()
    
    # вручную прописал user-agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36")
    # этот аргумент отключит сделает невидимым для сайтов работу WebDriver, не работает в режиме headless
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080") #работает в режиме headless
    # options.headless = True
    
    # инициализация драйвера
    s = Service(executable_path="/home/heyartem/PycharmProjects/Parsing_project/kuvalda_pars_selen/webdriver/chromedriver")
    driver = webdriver.Chrome(service=s, options=options)
    
    return driver


# запись cookies (ТОЛЬКО ДЛЯ ЗАПИСИ COOKIES)
def recording_cookies():
    
    url = "https://www.kuvalda.ru/"
    
    # инициализация драйвера
    driver = initialization_driver()
    
    try:
        driver.get(url=url)
        driver.maximize_window() # эта команда не работает в режиме headless, альтернатива "options.add_argument("--window-size=1920x1080")"        
        time.sleep(3)
        
        # кликаю на иконку "Личный кабинет", что бы ввести маил и пароль
        login_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header-top__login"))
        )
        
        # кликаю на нее
        login_button.click()
        time.sleep(2)
                    
        # нахожу поле ввода мэйла
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='auth_1']"))  # ищу по Тегу-"input", Атрибуту-"id; [@id='auth_1']-это предикат"            
        )
        email_input.clear()
        email_input.send_keys(user_name)  # ввожу емэил
        
        # нахожу поле ввода пароля
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='auth_2']"))
        )
        password_input.clear()
        password_input.send_keys(password)  # ввожу password
        
        # имитирую нажатие enter
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # сохраняю cookies в формате "user_name_cookies"                
        cookies_data = pickle.dump(driver.get_cookies(), open(f"{user_name}_cookies", "wb"))
        
        # инфоблок
        print(f'[INFO] cookies are written down')
        
        return cookies_data
        
     # блок, если будет ошибка
    except Exception as ex:
        print(ex)
        
    # обязательное закрытие вкладки, драйвера
    finally:
        driver.close()
        driver.quit()
    

# в фоновом режиме читает соxраненные cookies и получает данные пагинации, формирует формат рабочей ссылки
def activation_cookies_pagination(cookies_data):
    
    # ввод искомого инструмента
    # target = input("Привет введи, что именно ты ищещь (инструмент, лампы, лопаты): ")
    target = "шуруповерты"    # что бы не вводить поисковое слово во время тестирования
    
    url = "https://www.kuvalda.ru/"
   
    # инициализация драйвера
    driver = initialization_driver()
    
    try:
        driver.get(url=url)
        driver.maximize_window() # эта команда не работает в режиме headless, альтернатива "options.add_argument("--window-size=1920x1080")"
        time.sleep(3)
        
        # читаю сохраненные cookies
        for cookie in pickle.load(open(f"{user_name}_cookies", "rb")):
            driver.add_cookie(cookie)
        
        time.sleep(2)
        
        # обновление окна, для активации cookies
        driver.refresh()        
        time.sleep(3)
        
        # делаю скриншот
        driver.get_screenshot_as_file("scr_1.png")
        time.sleep(3)
        
        # нахожу строку поиска и ввожу искомое слово
        search_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search__input"))
        )
        search_input.clear()
        search_input.send_keys(target)  # ввел искомое слово
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # инфоблок
        print("[INFO] authorization is completed!")
        
        # скролл
        driver.execute_script("window.scrollTo(0, 4000)")
        time.sleep(2)
        
        # скролл до нижней части страницы
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
                
        # создаю директорию для сохранения страницы
        if not os.path.exists("data"):
            os.mkdir("data")
        
        # сохраняю страницу
        with open("data/1_data_selenium.html", "w") as file:
            file.write(driver.page_source)
        time.sleep(3)
        
        # так же сохранил данные страницы в переменную
        data = driver.page_source
        
        # создал объект BeautifulSoup
        soup = BeautifulSoup(data, "lxml")
        
        # получаю ссылку на последнюю страницу
        url = f'https://www.kuvalda.ru{soup.find_all("a", class_="pagination__item")[-1].get("href")}'
        
        """
        после ввода поискового слова "target", сайт формирует ссылки разного формата
        ссылка по запросу шуруповерты:
        	стр 1: https://www.kuvalda.ru/catalog/7309-shurupoverty/?keyword=шуруповерты
	        стр 2: https://www.kuvalda.ru/catalog/7309-shurupoverty/page-2/
         
         ссылка по запросу Диск:
        	стр 1: https://www.kuvalda.ru/catalog/search/?keyword=диск
	        стр 2: https://www.kuvalda.ru/catalog/search/page-2/?keyword=диск
        (некоторому оборудованию, он присваиват каталожный номер, например "/7309-shurupoverty/")
        
        После приведения к одному формату, ссылка будет выглядеть:
        	 https://www.kuvalda.ru/catalog/search/page-89/?keyword=диск
        	 https://www.kuvalda.ru/catalog/7309-shurupoverty/page-23/?keyword=шуруповерты
        """
        
        # если в ссылке нет слова "keyword", то оно подставляется в конце
        if 'keyword' not in url:
            url = f'{url}?keyword={target}'
            
            print("ready link: ", url)
            
        # пагинация, номер последней страницы  
        last_page_number = int(url.split('/')[-2].split('-')[1])  
        
        # инфоблок
        print(f'[INFO] Pages count: {last_page_number}')
        
        return url, last_page_number
    
    # блок, если будет ошибка
    except Exception as ex:
        print(ex)
        
    # обязательное закрытие вкладки, драйвера
    finally:
        driver.close()
        driver.quit()
        
        
# извлекаю наименование, прайс, старый прайс, ссылку
def collect_data(info_tuple, user_name):
    
    # переменная для записи в json
    all_json_data = []
    
    # переменная для записи в csv
    all_csv_data = []
    
    driver = initialization_driver()
    
    try:
        # формирую рабочие ссылки на каждую страницу
        # for page_number in range(1, info_tuple[1] + 1): # получаю числа от 1 до last_page_number
        for page_number in range(1, 5): # для тестового режима, что бы не проходить по всем страницам
            url_list = info_tuple[0].split('/')   # сплитанул рабочую ссылку по "/"
            
            # в рабочей ссылке у [-2] участника меняю число у 'page-..'
            url_list[-2] = f'page-{page_number}'
            
            # составил рабочую ссылку
            url = '/'.join(url_list)    
            
            # открываю первую страницу
            driver.get(url=url)            
            driver.maximize_window() # эта команда не работает в режиме headless, альтернатива "options.add_argument("--window-size=1920x1080")"
            time.sleep(2)            
            
            # инфоблок
            print(f"\n{20 * '*'}\n[INFO] start {url_list[-2]}") 
            
            # читаю сохраненные cookies
            for cookie in pickle.load(open(f"{user_name}_cookies", "rb")):
                driver.add_cookie(cookie)
            
            time.sleep(2)
            driver.refresh()
            time.sleep(3)
            
            # создаю объект BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "lxml")
            
            # нахожу общий блок скарточками
            block_cards = soup.find("div", id="add-content-block").find_all("div", class_="snippet__content")
            
            for card in block_cards:
                
                # наименование продукта
                try:
                    card_brend_dirty = card.find("a", class_="snippet__title").text
                    card_brend = " ".join(card_brend_dirty.split())
                except Exception as ex:
                    card_brend = "No data"
                    
                # прайс
                try:
                    card_price = card.find("span", class_="snippet__price-value").text
                except Exception as ex:
                    card_price = "No data"
                    
                # старый прайс, если есть
                try:
                    card_old_price = card.find("s", class_="snippet__price-old").text
                except Exception as ex:
                    card_old_price = "No data"
                    
                # ссылка на продукт
                try:
                    card_link = (f'https://www.kuvalda.ru{card.find("a").get("href")}')
                except Exception as ex:
                    card_link = "No data"
                
                # print(f'card_brend: {card_brend}\ncard_price: {card_price}\ncard_old_price: {card_old_price}\ncard_link: {card_link}\n{20 * " - "}')
                
                # упаковываю данные для записи в json
                all_json_data.append(
                    {
                        "card_brend": card_brend,
                        "card_price": card_price,
                        "card_old_price": card_old_price,
                        "card_link": card_link
                    }
                )
                
                # упаковываю данные для записи в csv
                all_csv_data.append(
                    [
                        card_brend,
                        card_price,
                        card_old_price,
                        card_link
                    ]
                )
            
             # инфоблок
            print(f"\n[INFO] completed {url_list[-2]}")            
   
    # блок, если будет ошибка
    except Exception as ex:
        print(ex)
        
    # обязательное закрытие вкладки, драйвера
    finally:
        driver.close()
        driver.quit()
        
    # записываю csv
    with open("data/data_csv_product.csv", "w") as file:
        writer = csv.writer(file) # создал писателя
        writer.writerow(   # записываю заголовки
            (
                "Name product",
                "Price",
                "Old_price",
                "Link"
            )
        )
        writer.writerows(all_csv_data)  #записываю значения
        
    # записываю json
    with open("data/data_json_product.json", "w") as file:
        json.dump(all_json_data, file, indent=4, ensure_ascii=False)
        
    # инфоблок
    print(f"[INFO] all code is done!")
            
        
def main():
    cookies_data = recording_cookies()
    info_tuple = activation_cookies_pagination(cookies_data)
    collect_data(info_tuple, user_name)
    

if __name__ == "__main__":
    main()
