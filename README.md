# Скрапинг данных при помощи Selenium <br/>https://www.kuvalda.ru


## Тех.детали: 
* _selenium ("headless", "--disable-blink-features=AutomationControlled, scroll")_ 
* _pickle_
* _os_
* _BeautifulSoup_
* _json_
* _csv_ 
* _split_
* _join_
<br/><br/>
<hr>

## Описание:
Скрипт открывает сайт, кликает иконку личный кабинет, вводит логин 
<br/>и пароль, сохраняет cookies, запрашивает у пользователя наименование
<br/>искомого инструмента, открывает сайт, активирует cookies, вводит 
<br/>искомое
<br/>слово, находит количество страниц, проходит по ним и собирает данные
<br/>(наименование, прайс, старый прайс, ссылку), записывает данные в 
<br/>json,csv. 
<br/>Скрипт может работать в фоновом (headless) режиме
<br/><br/>
<hr>

## Особенности:
после ввода поискового слова "target", сайт формирует ссылки разного <br/>формата
<br/>ссылка по запросу шуруповерты:
* стр 1: https://www.kuvalda.ru/catalog/7309-shurupoverty/?keyword=шуруповерты
* стр 2: https://www.kuvalda.ru/catalog/7309-shurupoverty/page-2/

<br/>ссылка по запросу Диск:
* стр 1: https://www.kuvalda.ru/catalog/search/?keyword=диск
* стр 2: https://www.kuvalda.ru/catalog/search/page-2/?keyword=диск
<br/>(некоторому оборудованию, он присваиват каталожный номер, например "/7309-shurupoverty/")

<br/> После приведения к одному формату, ссылка будет выглядеть:
* https://www.kuvalda.ru/catalog/search/page-89/?keyword=диск
* https://www.kuvalda.ru/catalog/7309-shurupoverty/page-23/?keyword=шуруповерты
<br/><br/>
<hr>

## Использование: 
- Основной фаил: main.py 
- если запускать в фоновом режиме (headless), закоментить "driver.
maximize_window()"(в 3-х местах) и раскоментить"options.headless = True", раскоментить строку ввода поискового слова "target"
- вписать свой логин и пароль, для авторизации на сайте
<br/><br/>
<hr>

