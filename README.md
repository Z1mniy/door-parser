# Инструкция по устновке парсера

## 1. склонируйте проект в любое удобное место на копьютере

```
cd /путь/до/удобной/папки
git clone https://github.com/Z1mniy/door-parser
```

---

## 2. перейдите в папку и скачайте все зависимости
```
cd door-parser
pip install -r requirments.txt
```

---

## 3. запустите файл main.py и начните использование

```
cd Папка_проекта
python main.py
```

---

## Управление:
- `-h` - команда для вывода подсказки
- `exit` - выход из программы
- ключ + сайт (написать можете, что удобнее)
    - `1` \ `https://labirintdoors.ru/`
    - `2` \ `https://bunkerdoors.ru/`
    - `3` \ `https://intecron-msk.ru/`
    - `4` \ `https://as-doors.ru/`
    - `5` \ `https://dveri-ratibor.ru/`
    - `6` \ `https://termo-door.ru/`
    - `7` \ `https://mxdoors.ru/`
    - `8` \ `https://xn--80aeahafcjmeq0c7ah.xn--p1ai/`
    - `9` \ `https://cmdoors.ru/`
    - `10` \ `https://closedoor.ru/`
    - `11` \ `https://str12.ru/`
    - `12` \ `https://forpostroznica.ru/`
    - `13` \ `https://doors007.ru/`

Программа умеет работать в многопоточном режиме, поэтому может обрабатывать несколько запросов параллельно для этого запросы надо вводить через пробел
т.е `1 8 3 9 5 6 13`