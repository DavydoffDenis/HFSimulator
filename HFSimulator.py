#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
import sys
import ui

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)  
        app_ui = ui.UserInterface()
        app_ui.init_ui()  # Первичная инициализация интерфейса пользователя без привязки к потоку симуляции канала и его параметрам
        app_ui.signals()  # Связывание пользовательского интерфейса и потока симуляции канала
        sys.exit(app.exec_())
    except RuntimeError:
        print("Проверяйте источники звука для симулятора!")