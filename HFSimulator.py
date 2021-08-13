#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
import sys
import ui
import logging
import time

if __name__ == '__main__':
    #logger_default_filename = f"HFS log {time.asctime()}"  # Задаём дефолтное имя для файла в который будут записываться логи
    # with open(logger_default_filename, "w") as logger:
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=logger_default_filename, level=logging.DEBUG)  # Первичная инициализация нашего логирования
    try:
        app = QApplication(sys.argv)  
        app_ui = ui.UserInterface()
        app_ui.init_ui()  # Первичная инициализация интерфейса пользователя без привязки к потоку симуляции канала и его параметрам
        app_ui.signals()  # Связывание пользовательского интерфейса и потока симуляции канала
        sys.exit(app.exec_())
    except RuntimeError:
        print("Проверяйте источники звука для симулятора!")
        #logging.critical("Не найдена звуковая карта Rubix44. Проверяйте источники звука для симулятора!")