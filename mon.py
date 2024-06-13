import requests
from colorama import init, Fore, Style
import time
import datetime
import os
from requests.exceptions import ConnectionError
from json import JSONDecodeError
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')   
init(autoreset=True)
start_time = time.time()
headers = {"user-agent": "Mozilla/5.0 (Linux; Android 13; Redmi Note 10S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"}
sellers_array = []
new_elements = []
timestamps = []
selection_array = []
yes = {'yes','y', ''}
no = {'no','n'}
r_r = 1
cached_data = None
a, a_b, a_p, s, s_b, s_p, r = 0, 0, 0, 0, 0, 0, 0
a_int, a_b_int, a_p_int, r_int, s_int, s_b_int, s_p_int = 0, 0, 0, 0, 0, 0, 0
startnow = config.get("Settings", "startnow")
if startnow in no:
    useconf = input("Использовать конфиг? (Y/n): ")
    if useconf in yes:
        trafficType = input("Введите цифру типа трафика (1-ГБ, 2-минуты, 3-SMS): ")
        traffic_types = {"1": "data", "2": "voice", "3": "sms"}
        trafficType = traffic_types.get(trafficType, trafficType)
        volume = int(input('Введите кол-во ГБ/минут/SMS: '))
        mincost = input("Минималка? (Y/n): ").lower()
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
        delete = input('Обнулить лог-файл? (Y/n): ').lower()
        mincost = input("Минималка? (Y/n): ").lower()
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
    if mincost in yes:   
        cost_url = f"https://tele2.ru/api/exchange/lots/stats/volumes?trafficType={trafficType}"
        try:
            response = requests.get(cost_url, headers=headers)
            data = response.json()
        except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
            print(Fore.YELLOW + 'Потеряно соединение с сервером')
            time.sleep(10)
            pass
        def get_cost(volume):
            for item in data['data']:
                if item['volume'] == volume:
                    cost = item["minCost"]
                    return cost
            return None
        cost = int(get_cost(volume))
    elif mincost in no:
        cost = int(input("Введите цену лота: "))
else:
    interval = config.getint("Settings", "interval")
    delay = config.getint("Settings", "delay")
    delete = config.get("Settings", "delete")
    interval *= 60
    trafficType = config.get("Settings", "trafficType")
    traffic_types = {"1": "data", "2": "voice", "3": "sms"}
    trafficType = traffic_types.get(trafficType, trafficType)
    volume = config.getint("Settings", "volume")
    mincost = config.get("Settings", "mincost")
    if mincost in no:
        cost = config.getint("Settings", "cost")
    else:
        cost_url = f"https://tele2.ru/api/exchange/lots/stats/volumes?trafficType={trafficType}"
        try:
            response = requests.get(cost_url, headers=headers)
            data = response.json()
        except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
            print(Fore.YELLOW + 'Потеряно соединение с сервером')
            time.sleep(10)
            pass
            def get_cost(volume):
                for item in data['data']:
                    if item['volume'] == volume:
                        cost = item["minCost"]
                        return cost
                return None
            cost = int(get_cost(volume))
    
while True:    
    
    trafficTypeFile = "gb" if trafficType == "data" else "min" if trafficType == "voice" else "sms"
    if delete in yes:
        open(f"sales_{volume}{trafficTypeFile}_{cost}p.txt", "w").close()
        break
    elif delete in no:
        break

try:
    response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=5000", headers=headers, timeout=5)
    data = response.json()
except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
    print(Fore.YELLOW + 'Потеряно соединение с сервером')
    time.sleep(10)
    pass
for item in reversed(data["data"]):
    seller = item.get("seller", {})
    name = seller.get("name")
    emojis = seller.get("emojis")
    id = item.get("id")
    my = item.get("my")
    seller_list = ["Анонимный продавец", emojis, str(id), str(my)] if name is None else [name, emojis, str(id), str(my)]
    sellers_array.insert(0, seller_list)
    timestamps.insert(0, time.time())
def check(id):
    global cached_data
    if not cached_data:
        try:
            response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&&limit=500", headers=headers, timeout=5)
            cached_data = response.json()
        except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
            print(Fore.YELLOW + 'Потеряно соединение с сервером')
            time.sleep(10)
            pass
    try:
        for item in cached_data["data"]:
            id_check = item.get("id")
            cost_change = item.get("cost").get("amount")
            if id_check == id:
                return True, cost_change
    except Exception as e:
        print(Fore.YELLOW + f'Нет данных для обработки. Ошибка: {e}')
    return False, None
trafficTypeVisual = " ГБ" if trafficType == "data" else " минут(ы)" if trafficType == "voice" else " SMS"
if a == 0:
    k = round((s_p/(a+1+r))*100, 1)
else:
    k = round((s_p/(a+r))*100, 1)

while True:
    if a == 0:
        k = round((s_p/(a+1+r))*100, 1)
    else:
        k = round((s_p/(a+r))*100, 1)
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > interval:
        with open(f"stats_{volume}{trafficTypeFile}_{cost}p.txt", "a", encoding="utf-8") as f:
            f.write(f'Статистика за {round(interval / 60)} минут{ending}:\n')
            f.write('Выставлено лотов: ' + str(a - a_int) + '\n – Ботами: ' + str(a_b - a_b_int) + '\n – Продавцами: ' + str(a_p - a_p_int))
            f.write('\nПродано лотов: ' + str(s - s_int) + '\n – Ботами: ' + str(s_b - s_b_int) + '\n – Продавцами: ' + str(s_p - s_p_int) + '\nРакет: ' + str(r - r_int) + "\nКоэффициент: " + str(k) + "\n" + '--------------------------------------------------------\n')
        start_time += interval
        a_int, a_b_int, a_p_int, r_int = a, a_b, a_p, r
        s_int, s_b_int, s_p_int = s, s_b, s_p
    os.system('cls' if os.name == 'nt' else 'clear')
   
    print(Fore.WHITE + f"Лот: {volume}{trafficTypeVisual}. " + f"Цена: {str(cost).replace('.0', '')} ₽.")
    print(Fore.YELLOW + 'Выставлено лотов: ' + str(a) + '. Ботами: ' + str(a_b) + '. Продавцами: ' + str(a_p) + Fore.CYAN + ' | Ракет: ' + str(r))
    print(Fore.GREEN + 'Продано лотов: ' + str(s) + '. Ботами: ' + str(s_b) + '. Продавцами: ' + str(s_p))
    print(Fore.CYAN + "Коэффициент: " + str(k))
    print('---------------------------------------------------------')    
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
    except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
        print(Fore.YELLOW + 'Потеряно соединение с сервером')
        time.sleep(10)
        continue
    print('---------------------------------------------------------')
   
    try:
        response = requests.get(f"https://tele2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=300", headers=headers, timeout=5)
        data = response.json()
    except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
        print(Fore.YELLOW + 'Потеряно соединение с сервером')
        time.sleep(10)
        continue
    new_elements = []
    selection_array = []
    for item in reversed(data["data"]):
        seller = item.get("seller", {})
        name = seller.get("name")
        emojis = seller.get("emojis")
        id = item.get("id")
        my = item.get("my")
        seller_list = ["Анонимный продавец", emojis, str(id), str(my)] if name is None else [name, emojis, str(id), str(my)]
        selection_array.insert(0, seller_list)
        if seller_list[-2] not in [element[-2] for element in sellers_array]:
            new_elements.insert(0, seller_list)
            a += 1
            sellers_array.insert(0, seller_list)
            timestamps.insert(0, time.time())
            value = seller_list[-1]
            if value == 'True':
                a_b += 1
            elif value == 'False':
                a_p += 1
        else:
            for i, element in enumerate(sellers_array):
                if element[-2] == seller_list[-2] and element[0] != seller_list[0]:                    
                    sellers_array[i] = seller_list
                    break
    if len(new_elements) > 0:
        print(f"Добавлен(ы) лот(ы): ")
        for element in new_elements:
            if element[-1] == 'True':
                print(Fore.RED + str(element[0]))
            else:
                print(Fore.GREEN + str(element[0]))
    with open(f"sales_{volume}{trafficTypeFile}_{cost}p.txt", "a", encoding="utf-8") as f:
        for element in sellers_array[:20]:
            id = element[-2]
            if id not in [element[-2] for element in selection_array]:
                pos = sellers_array.index(element) - len(new_elements) + 1
                timestamp_index = [element[-2] for element in sellers_array].index(id)
                timestamp = timestamps[timestamp_index]
                if (element[-1] == 'True' and 0 <= time.time() - timestamp <= 3600):
                    print("Продан(ы) лот(ы). Позиция: " + str(pos))
                    print(Fore.RED + str(element[0]) + ' ' + str(element[1]))
                    f.write(str(element[0]) + ' - Бот. Время продажи: {}'.format(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
                    s_b += 1; s += 1
                elif (element[-1] == 'True' and time.time() - timestamp > 3600):
                    print('Лот сгорел. Позиция: ' + str(pos))
                    print(Fore.RED + str(element[0]) + ' ' + str(element[1]))
                elif element[-1] == 'False':
                    result, cost_change = check(id)
                    if not result:
                        print("Продан(ы) лот(ы). Позиция: " + str(pos))
                        print(Fore.GREEN + str(element[0]) + ' ' + str(element[1]))
                        f.write(str(element[0]) + ' - Продавец. Время продажи: {}'.format(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
                        s_p += 1; s += 1                
                    else:
                        print(Fore.GREEN + str(element[0]) + ' - Продавец изменил цену на ' + str(int(cost_change)) + " ₽")
                sellers_array.remove(element)
                timestamps.pop(timestamp_index)
                r_r += 1
    for element in selection_array[:15]:
        if element in sellers_array and sellers_array.index(element) - selection_array.index(element) > r_r:
            r += 1
            old_index = sellers_array.index(element)
            new_index = selection_array.index(element)
            sellers_array.remove(element)
            sellers_array.insert(new_index, element)
            value_to_move = timestamps.pop(old_index)
            timestamps.insert(new_index, value_to_move)
            if element[-1] == 'False':
                print('Ракета: ' + Fore.GREEN + str(element[0]) + ' ' + str(element[1]) + '  ' + Fore.WHITE + str(old_index + 1) + ' --------> ' + str(new_index + 1))
    sellers_array = sellers_array[:100000]
    timestamps = timestamps [:100000]
    cached_data = None
    r_r = 1
    time.sleep(delay)
