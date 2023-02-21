from datetime import datetime
import time
import keyboard
import logging
import configparser
import sqlite3
import os

#Создание таблицы в базе SQLite
con = sqlite3.connect("Kettle_db")
cursor = con.cursor()
try:
    cursor.execute("""CREATE TABLE kettle_info
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    log TEXT)
    """)
except:
    pass

#Инициализация конфигурационного файла и логгера
config = configparser.ConfigParser()
config.read("settings.ini")
logging.basicConfig(level=logging.INFO, filename="kettle.log", filemode='w')

#Функция логирования, вывода информации на консоль и сохранения в базу данных
def print_and_logging(message):
    print(message)
    logging.info(message)
    data = (datetime.now().strftime("%H:%M:%S"), message)
    cursor.execute('INSERT INTO kettle_info (date, log) VALUES (?, ?)', data)
    con.commit()

class Kettle:
    button = False
    water = float(config['Water']['water'])             # Начальное количество воды
    boiling_time = int(config['Time']['boiling_time'])  # Время кипения (в секундах)
    temp = int(config['Temperature']['temp'])           # Температура чайника, приблизительно равна комнатной
    max_temp = int(config['Temperature']['max_temp'])   # Максимальная температура, при которой чайник отключается
    max_volume = float(config['Water']['max_volume'])   # Максимальное количество воды в чайнике"""

    def __init__(self):
        if self.water > self.max_volume:    #Начальный объем воды в чайнике не может быть
            self.water = 0                  #больше максимального
            self.max_volume = 1.0

    def boil(self):
        current_time = self.boiling_time
        while current_time > 0:
            if self.button:
                print(self.temp)
                current_time -= 1

                '''Ручное выключение чайника.
                Данный цикл нужен, чтобы программа могла успеть считать
                нажатие клавиши на протяжении 1 секунды'''
                for a in range(10):
                    time.sleep(0.1)
                    if keyboard.is_pressed('s'):
                        self.button = False
                        message = f"Чайник остановлен, температура: {self.temp} градуса!"
                        print_and_logging(message)
                        exit()

                #Отключение чайника при достижении максимальной температуры
                if self.temp >= self.max_temp:
                    self.button = False
                    message = f"Чайник вскипел и был выключен, температура составляет {self.temp} градусов'"
                    print_and_logging(message)
                    exit()

                '''Температура повышается в соотношении % от максимальной температуры / единица времени кипения
                                Для того, чтобы можно было менять и макс.температуру, и время кипения.'''
                self.temp += self.max_temp * 0.1 / (self.boiling_time * 0.1)

        #Отключение чайника по истечению времени
        self.button = False
        message = f"Чайник вскипел и был выключен, температура составляет {self.temp} градусов"
        print_and_logging(message)


if __name__ == '__main__':
    # Инициализация чайника
    kettle_instance = Kettle()
    print(f'Пожалуйста, налейте воды в чайник. Текущий объем: {kettle_instance.water}.\n'
          f'Максимальный объем: {kettle_instance.max_volume}')

    # Набираем в чайник воды
    volume = 0       #Количество набираемой воды, вместе с текущим объемом не должно превышать максимальный
    while volume <= 0 or volume + kettle_instance.water > kettle_instance.max_volume:
        try:
            volume = float(input(f'Укажите количество воды до {kettle_instance.max_volume - kettle_instance.water}: \n'))
            if 0 < volume <= Kettle.max_volume - Kettle.water:
                kettle_instance.water += volume
                break
        except Exception:
            print("Неверное значение.")

    message = f'В чайник была налита вода в объеме {volume}, текущий объем: {round(kettle_instance.water, 2)} литра.'
    print_and_logging(message)
    print('Нажмите кнопку \'s\' для включения/выключения чайника...')

    # Включение чайника по кнопке S
    statement = None
    while statement != 's':
        statement = input()
        if statement == 's':
            Kettle.button = True
            message = "Чайник включен"
            print_and_logging(message)
            kettle_instance.boil()
        else:
            print('Неверный ввод. Пожалуйста, повторите попытку.')
