import requests
from colorama import init, Fore, Style
import time
import datetime
import os
from requests.exceptions import JSONDecodeError, ConnectionError
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')   
init(autoreset=True)
start_time = time.time()
headers = {"user-agent": "Mozilla/5.0 (Linux; Android 13; Redmi Note 10S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"}
sellers_array = []
new_elements = []
selection_array = []
yes = {'yes','y', ''}
no = {'no','n'}
a, a_b, a_p, s, s_b, s_p, r = 0, 0, 0, 0, 0, 0, 0
a_int, a_b_int, a_p_int, r_int, s_int, s_b_int, s_p_int = 0, 0, 0, 0, 0, 0, 0
useconf = input("Использовать конфиг? (Y/n): ")
if useconf in yes:
    trafficType = input("Введите цифру типа трафика (1-ГБ, 2-минуты, 3-SMS): ")
    traffic_types = {"1": "data", "2": "voice", "3": "sms"}
    trafficType = traffic_types.get(trafficType, trafficType)
    volume = int(input('Введите кол-во ГБ/минут/SMS: '))
    interval = config.getint("Settings", "interval")
    delay = config.getint("Settings", "delay")
    delete = config.get("Settings", "delete")
    interval *= 60
else:
    writeconf = input("Запомнить настройки? (Y/n): ")
    trafficType = input("Введите цифру типа трафика (1-ГБ, 2-минуты, 3-SMS): ")
    traffic_types = {"1": "data", "2": "voice", "3": "sms"}
    trafficType = traffic_types.get(trafficType, trafficType)
    volume = int(input('Введите кол-во ГБ/минут: '))
    interval = int(input('За какой интервал собирать статистику (в минутах): ')) * 60   
    delay = int(input('Введите частоту обновления (в секундах): '))
    delete = input('Обнулить файл? (Y/n): ').lower()
    if writeconf in yes:
        config.set("Settings", "interval", str(round(interval/60)))
        config.set("Settings", "delay", str(delay))
        config.set("Settings", "delete", delete)
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
if 10 < interval / 60 % 100 < 20:
    ending = ""
elif interval / 60 % 10 == 1:
    ending = "у"
elif interval /60 % 10 in [2, 3, 4]:
    ending = "ы"
else:
    ending = ""
    
while True:    

    if delete in yes:
        open("sales.txt", "w").close()
        break
    elif delete in no:
        break
try:
   response = requests.get(f"https://tele2.ru/api/exchange/lots/stats/volumes?trafficType={trafficType}", headers=headers)
   data = response.json()
except (JSONDecodeError, ConnectionError):
    print(Fore.YELLOW + 'Нет связи с сервером')
def get_cost(volume):
        for item in data['data']:
            if item['volume'] == volume:
                cost = item["minCost"]
                return cost
        return None
cost = get_cost(volume)
try:
    response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=100", headers=headers)
    data = response.json()
except (JSONDecodeError, ConnectionError):
    print(Fore.YELLOW + 'Нет связи с сервером')
for item in reversed(data["data"]):
    seller = item.get("seller", {})
    name = seller.get("name")
    emojis = seller.get("emojis")
    id = item.get("id")
    my = item.get("my")
    seller_list = ["Анонимный продавец", ''.join(emojis), str(id), str(my)] if name is None else [name, ''.join(emojis), str(id), str(my)]
    sellers_array.insert(0, seller_list)

def check(id):
    for i in range(4):
        try:
            response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost + i}&limit=4", headers=headers)
            data = response.json()
        except (JSONDecodeError, ConnectionError):
            print(Fore.YELLOW + 'Нет связи с сервером')
        for item in data["data"]:
            id_check = item.get("id")
            if id_check == id:
                return True
        time.sleep(0.3)
    return False
trafficTypeVisual = " ГБ" if trafficType == "data" else " минут(ы)" if trafficType == "voice" else " SMS"
while True:
    current_time = time.time()
    elapsed_time = current_time - start_time
    if a == 0:
        k = round((s_p/(a+1))*100, 1)
    else:
        k = round((s_p/a)*100, 1)
    if elapsed_time > interval:
        with open("sales.txt", "a", encoding="utf-8") as f:
            f.write('--------------------------------------------------------\n' + f'Статистика за {round(interval / 60)} минут{ending}:\n')
            f.write(f"Лот: {volume}{trafficTypeVisual}. ")
            f.write('Выставлено лотов: ' + str(a - a_int) + '. Ботами: ' + str(a_b - a_b_int) + '. Продавцами: ' + str(a_p - a_p_int) + ' | Ракет: ' + str(r - r_int) + "\n")
            f.write('Продано лотов: ' + str(s - s_int) + '. Ботами: ' + str(s_b - s_b_int) + '. Продавцами: ' + str(s_p - s_p_int) + "\n" + "Коэффициент: " + str(k) + '--------------------------------------------------------\n\n')
            start_time += interval
        a_int, a_b_int, a_p_int, r_int = a, a_b, a_p, r
        s_int, s_b_int, s_p_int = s, s_b, s_p
        print(interval)
    os.system('cls' if os.name == 'nt' else 'clear')
   
    print(Fore.WHITE + f"Лот: {volume}{trafficTypeVisual}. " + f"Цена: {str(cost).replace('.0', '')} ₽.")
    print(Fore.YELLOW + 'Выставлено лотов: ' + str(a) + '. Ботами: ' + str(a_b) + '. Продавцами: ' + str(a_p) + Fore.CYAN + ' | Ракет: ' + str(r))
    print(Fore.GREEN + 'Продано лотов: ' + str(s) + '. Ботами: ' + str(s_b) + '. Продавцами: ' + str(s_p))
    print(Fore.CYAN + "Коэффициент: " + str(k))
    print('-------------------------------------------------')    
    counter = 0
    try:
        for item in data["data"][:15]:
            seller = item.get("seller", {})
            name = seller.get("name")
            emojis = seller.get("emojis")
            trafficType = item.get("trafficType")
            my = item.get("my")
            emoji_dict = {"devil": "\U0001F608", "cool": "\U0001F60E", "cat": "\U0001F431", "zipped": "\U0001F910", "scream": "\U0001F631", "rich": "\U0001F911", "tongue": "\U0001F61B", "bomb": "\U0001F4A3", "": "  "}

            for i in range(len(emojis)):
                emojis[i] = emoji_dict[emojis[i]]

            name = "Анонимный продавец" if name is None else name
            if my is False:
                name = Fore.GREEN + str(name)
                emojis = Fore.GREEN + str(emojis)
            else:
                name = Fore.RED + str(name)
                emojis = Fore.RED + str(emojis)

            counter += 1
            if counter <= 9:
                print(str(counter) + '.  ' + f"{Fore.WHITE}{name:<25}{emojis}")
            elif counter > 9:
                print(str(counter) + '. ' + f"{Fore.WHITE}{name:<25}{emojis}")
    except KeyError:
        print(Fore.YELLOW + "Произошла ошибка при обработке данных. Возможен бан по IP, или временная потеря связи с сервером.")
        pass
    print('-------------------------------------------------')
   
    try:
        response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=26", headers=headers)
        data = response.json()
    except (JSONDecodeError, ConnectionError):
        print(Fore.YELLOW + 'Нет связи с сервером')
        continue
    new_elements = []
    selection_array = []
    for item in reversed(data["data"]):
        seller = item.get("seller", {})
        name = seller.get("name")
        emojis = seller.get("emojis")
        id = item.get("id")
        my = item.get("my")
        seller_list = ["Анонимный продавец", ''.join(emojis), str(id), str(my)] if name is None else [name, ''.join(emojis), str(id), str(my)]
        selection_array.insert(0, seller_list)
        if seller_list[-2] not in [element[-2] for element in sellers_array]:
            new_elements.insert(0, seller_list)
            a += 1
            sellers_array.insert(0, seller_list)
            value = seller_list[-1]
            if value == 'True':
                a_b += 1
            elif value == 'False':
                a_p += 1
    if len(new_elements) > 0:
        print(f"Добавлен(ы) лот(ы): ")
        for element in new_elements:
            if element[-1] == 'True':
                print(Fore.RED + str(element[0:2]))
            else:
                print(Fore.GREEN + str(element[0:2]))
    for element in selection_array[:4]:
        if element in sellers_array[4:] and sellers_array.index(element) - selection_array.index(element) >= 3:
            r += 1
            old_index = sellers_array.index(element)
            new_index = selection_array.index(element)
            sellers_array.remove(element)
            sellers_array.insert(new_index, element)
            print('Ракета!' + Fore.RESET)
            if element[-1] == 'True':
                print(Fore.RED + str(element[0:2]) + ' | ' + str(old_index + 1) + ' --------> ' + str(new_index + 1))
            else:
                print(Fore.GREEN + str(element[0:2]) + ' | ' + str(old_index + 1) + ' --------> ' + str(new_index + 1))
    with open("sales.txt", "a", encoding="utf-8") as f:
        for element in sellers_array[:20]:
            id = element[-2]
            if id not in [element[-2] for element in selection_array]:
                if not check(id):
                    pos = sellers_array.index(element) - len(new_elements) + 1
                    print('Продан(ы) лот(ы). ' + "Позиция: " + str(pos))
                    if element[-1] == 'True':
                        print(Fore.RED + str(element[0:2]))
                        f.write(f"Лот: {volume}{trafficTypeVisual}. " + str(element[0]) + ' - Бот. Время продажи: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.")) + " Продан с " + str(pos) + " позиции" + "\n")
                        s_b += 1
                    else:
                        print(Fore.GREEN + str(element[0:2]))                      
                        f.write(f"Лот: {volume}{trafficTypeVisual}. " + str(element[0]) + ' - Продавец. Время продажи: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.")) + " Продан с " + str(pos) + " позиции" + "\n")
                        s_p += 1
                    sellers_array.remove(element)
                    s += 1
                else:
                    print(Fore.GREEN + str(element[0]) + ' - Продавец изменил цену.')
                    sellers_array.remove(element)
    sellers_array = sellers_array[:1000]
    time.sleep(delay)