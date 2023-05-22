

import parameters_handler
from PyQt5.QtWidgets import (QWidget, QMainWindow, QTextEdit, QApplication,
                             QPushButton, QAction, qApp, QLineEdit, QFileDialog,
                             QGroupBox, QLabel, QDoubleSpinBox, QSpinBox,
                             QHBoxLayout, QVBoxLayout, QGridLayout, QLayout, QComboBox)
from PyQt5.QtGui import QIcon, QTextCursor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal

# import simulation

import ch1_simulation
import ch2_simulation
# import ch3_simulation
# import ch4_simulation

import functools
import epoll_server_multy
import sys
import csv
import os.path
from contextlib import redirect_stdout

class UserInterface(QMainWindow):
    
    def __init__(self):
        super(QMainWindow, self).__init__()
        # self.sim_t = simulation.simulation()  # Создаем экземпляр класса потока выполнения симуляции канала
        # self.sim_t = simulation_test.simulation_test()  # Создаем экземпляр класса потока выполнения симуляции канала для тестирования без внешней звуковой карты
        self.ch1_sim_t = ch1_simulation.ch1_simulation()
        self.ch2_sim_t = ch2_simulation.ch2_simulation()
        # self.ch3_sim_t = ch3_simulation.ch3_simulation()
        # self.ch4_sim_t = ch4_simulation.ch4_simulation()
        
        self.sim_handler1 = parameters_handler.Parameters(self.ch1_sim_t, self.ch2_sim_t)  # Создаем экземпляр класса обслуживающего поток симуляции  
        # self.sim_handler2 = parameters_handler.Parameters(self.ch3_sim_t, self.ch4_sim_t)

        self.adapt_mode = epoll_server_multy.ServerHandler()
        self.teamwork = False
        
    def init_ui(self):
        lbl1_beams = QLabel("Амплитуда")
        lbl2_beams = QLabel("Первый луч:")
        lbl3_beams = QLabel("Второй луч:")
        lbl4_beams = QLabel("Зад. меж. луч.:")
        lbl5_beams = QLabel("мс")
        lbl1_1_beams = QLabel("Амплитуда")
        lbl2_1_beams = QLabel("Первый луч:")
        lbl3_1_beams = QLabel("Второй луч:")
        lbl4_1_beams = QLabel("Зад. меж. луч.:")
        lbl5_1_beams = QLabel("мс")
        
        lbl6_beams = QLabel("Амплитуда первого луча:")
        lbl7_beams = QLabel("Амплитуда второго луча:")
        lbl6_1_beams = QLabel("Амплитуда первого луча:")
        lbl7_1_beams = QLabel("Амплитуда второго луча:")
        self.lbl8_beams = QLabel("-")
        self.lbl9_beams = QLabel("-")
        self.lbl10_beams = QLabel("-")
        self.lbl11_beams = QLabel("-")
        lbl12_beams = QLabel("Задержка между лучами:")
        lbl12_1_beams = QLabel("Задержка между лучами:")
        self.lbl13_beams = QLabel("-")
        self.lbl14_beams = QLabel("-")
        lbl15_beams = QLabel("мс")
        lbl15_1_beams = QLabel("мс")

        lbl1_doppler = QLabel("Доп. сдвиг:")
        lbl2_doppler = QLabel("Доп.  уширение:")
        lbl3_doppler = QLabel("Гц")
        lbl4_doppler = QLabel("Гц")
        lbl5_doppler = QLabel("                          Доплеровский сдвиг:")
        lbl6_doppler = QLabel("                          Доплеровское  уширение:")
        lbl1_1_doppler = QLabel("Доп. сдвиг:")
        lbl2_1_doppler = QLabel("Доп.  уширение:")
        lbl3_1_doppler = QLabel("Гц")
        lbl4_1_doppler = QLabel("Гц")
        lbl5_1_doppler = QLabel("Доплеровский сдвиг:")
        lbl6_1_doppler = QLabel("Доплеровское  уширение:")
        
        self.lbl7_doppler = QLabel("-")
        self.lbl8_doppler = QLabel("-")
        lbl9_doppler = QLabel("Гц")
        lbl10_doppler = QLabel("Гц")
        self.lbl7_1_doppler = QLabel("-")
        self.lbl8_1_doppler = QLabel("-")
        lbl9_1_doppler = QLabel("Гц")
        lbl10_1_doppler = QLabel("Гц")

        lbl1_snr = QLabel("ОСШ")
        lbl2_snr = QLabel("дБ")
        lbl3_snr = QLabel("                          ОСШ установленное:")
        self.lbl4_snr = QLabel("-")
        lbl5_snr = QLabel("дБ")
        lbl1_1_snr = QLabel("ОСШ")
        lbl2_1_snr = QLabel("дБ")
        lbl3_1_snr = QLabel("ОСШ установленное:")
        self.lbl4_1_snr = QLabel("-")
        lbl5_1_snr = QLabel("дБ")
        lbl6_snr = QLabel("ОСШ прямой канал:")
        self.lbl7_snr = QLabel("-")
        lbl8_snr = QLabel("дБ")
        lbl9_snr = QLabel("                          ОСШ обратный канал:")
        self.lbl10_snr = QLabel("-")
        lbl11_snr = QLabel("дБ")
        lbl12_snr = QLabel("ОСШ прямой канал:")
        self.lbl13_snr = QLabel("-")
        lbl14_snr = QLabel("дБ")
        lbl15_snr = QLabel("ОСШ обратный канал:")
        self.lbl16_snr = QLabel("-")
        lbl17_snr = QLabel("дБ")

        # Коммутация
        lbl1_commutation = QLabel("Прямой канал:")
        lbl2_commutation = QLabel("Вход:")
        lbl3_commutation = QLabel("Выход:")
        lbl4_commutation = QLabel("Обратный канал:")
        lbl5_commutation = QLabel("Вход:")
        lbl6_commutation = QLabel("Выход:")
        lbl7_commutation = QLabel("Прямой канал:")
        lbl8_commutation = QLabel("Вход:")
        lbl9_commutation = QLabel("Выход:")
        lbl10_commutation = QLabel("Обратный канал:")
        lbl11_commutation = QLabel("Вход:")
        lbl12_commutation = QLabel("Выход:")
        
        
        lbl1_rms = QLabel("RMS прямого канала:")
        lbl1_1_rms = QLabel("RMS прямого канала:")
        self.lbl2_rms = QLabel("-")
        self.lbl3_rms = QLabel("-")
        lbl4_rms = QLabel("                          RMS обратного канала:")
        lbl4_1_rms = QLabel("RMS обратного канала:")
        self.lbl5_rms = QLabel("-")
        self.lbl6_rms = QLabel("-")
#         self.lbl5_rms = QLabel("Симулятор находится в режиме ожидания.")

        lbl1_freq_adapt_mode = QLabel("Адрес сервера:")
        lbl2_freq_adapt_mode = QLabel("Номер порта:")
        lbl3_freq_adapt_mode = QLabel("Адрес модема 1:")        
        lbl4_freq_adapt_mode = QLabel("Адрес модема 2:")
        lbl5_freq_adapt_mode = QLabel("Адрес модема 3:")        
        lbl6_freq_adapt_mode = QLabel("Адрес модема 4:")
        lbl7_freq_adapt_mode = QLabel("Набор каналов:")
        self.lbl8_freq_adapt_mode = QLabel("parameters_for_sim.csv")
        self.channels_csv_filename = "parameters_for_sim.csv"
        lbl9_freq_adapt_mode = QLabel("Набор каналов 2:")
        self.lbl10_freq_adapt_mode = QLabel("parameters_for_sim.csv")
        self.channels_csv_filename2 = "parameters_for_sim2.csv"
        
        lbl1_about = QLabel()
        pixmap = QPixmap("polet.png")
        lbl1_about.setPixmap(pixmap)
        lbl2_about = QLabel("Версия: 2.0")
        lbl3_about = QLabel("Авторы проекта: Алексей Львов, Денис Давыдов")
        lbl4_about = QLabel('АО "НПП "Полет", 2019-2023 г.')
        
        self.txt1_term_output = QTextEdit()  # Поле вывода сообщений симулятора
        self.txt1_term_output.setReadOnly(True)
        self.txt1_term_output.setMinimumWidth(500)
        
        sys.stdout = OutputLogger(emit_write = self.append_log)
        sys.stderr = OutputLogger(emit_write = self.append_log)
#         stdout_fd = sys.stdout.fileno()
#         f = open('output.txt', 'w')        
#         redirect_stdout(f)
        
        # Для первой пары модемов

        self.dbl1_beams = QDoubleSpinBox()    # Амплитуда первого луча
        self.dbl1_beams.setMaximum(1.0)
        self.dbl1_beams.setMinimum(0)
        self.dbl1_beams.setValue(1.0)
        self.dbl1_beams.setSingleStep(0.1)

        self.dbl2_beams = QDoubleSpinBox()    # Амплитуда второго луча
        self.dbl2_beams.setMaximum(1.0)
        self.dbl2_beams.setMinimum(0)
        self.dbl2_beams.setValue(1.0)
        self.dbl2_beams.setSingleStep(0.1)

        self.dbl3_beams = QDoubleSpinBox()    # Временной сдвиг второго луча относительно первого
        self.dbl3_beams.setMaximum(10)
        self.dbl3_beams.setMinimum(0)
        self.dbl3_beams.setValue(2.0)
        self.dbl3_beams.setSingleStep(0.1)

        # Для второй пары модемов

        self.dbl4_beams = QDoubleSpinBox()    # Амплитуда первого луча
        self.dbl4_beams.setMaximum(1.0)
        self.dbl4_beams.setMinimum(0)
        self.dbl4_beams.setValue(1.0)
        self.dbl4_beams.setSingleStep(0.1)

        self.dbl5_beams = QDoubleSpinBox()    # Амплитуда второго луча
        self.dbl5_beams.setMaximum(1.0)
        self.dbl5_beams.setMinimum(0)
        self.dbl5_beams.setValue(1.0)
        self.dbl5_beams.setSingleStep(0.1)

        self.dbl6_beams = QDoubleSpinBox()    # Временной сдвиг второго луча относительно первого
        self.dbl6_beams.setMaximum(10)
        self.dbl6_beams.setMinimum(0)
        self.dbl6_beams.setValue(2.0)
        self.dbl6_beams.setSingleStep(0.1)

        # Для первой пары модемов

        self.dbl1_doppler = QDoubleSpinBox()  # Доплеровоский сдвиг лучей в формате с плавающей точкой
        self.dbl1_doppler.setMaximum(75)
        self.dbl1_doppler.setMinimum(-75)
        self.dbl1_doppler.setSingleStep(1)

        self.dbl2_doppler = QDoubleSpinBox()  # Доплеровское рассеивание (уширение)
        self.dbl2_doppler.setMaximum(30)
        self.dbl2_doppler.setMinimum(0)
        self.dbl2_doppler.setValue(1.0)
        self.dbl2_doppler.setSingleStep(0.1)

        # Для второй пары модемов

        self.dbl3_doppler = QDoubleSpinBox()  # Доплеровоский сдвиг лучей в формате с плавающей точкой
        self.dbl3_doppler.setMaximum(75)
        self.dbl3_doppler.setMinimum(-75)
        self.dbl3_doppler.setSingleStep(1)

        self.dbl4_doppler = QDoubleSpinBox()  # Доплеровское рассеивание (уширение)
        self.dbl4_doppler.setMaximum(30)
        self.dbl4_doppler.setMinimum(0)
        self.dbl4_doppler.setValue(1.0)
        self.dbl4_doppler.setSingleStep(0.1)

        # Для первой пары модемов

        self.dbl1_snr = QDoubleSpinBox()  # Отношение сигнал-шум
        self.dbl1_snr.setMaximum(40)
        self.dbl1_snr.setMinimum(-20)
        self.dbl1_snr.setValue(10)
        self.dbl1_snr.setSingleStep(1)
        
        # Для второй пары модемов

        self.dbl2_snr = QDoubleSpinBox()  # Отношение сигнал-шум
        self.dbl2_snr.setMaximum(40)
        self.dbl2_snr.setMinimum(-20)
        self.dbl2_snr.setValue(10)
        self.dbl2_snr.setSingleStep(1)
        
        
        self.int1_m_addr = QSpinBox()  # Адрес первого модема
        self.int1_m_addr.setValue(12)
        
        self.int2_m_addr = QSpinBox()  # Адрес второго модема
        self.int2_m_addr.setValue(13)

        self.int3_m_addr = QSpinBox()  # Адрес третьего модема
        self.int3_m_addr.setValue(14)
        
        self.int4_m_addr = QSpinBox()  # Адрес четвёртого модема
        self.int4_m_addr.setValue(15)
        
        self.int_serv_port = QSpinBox()  # Порт на котором слушает сервер
        self.int_serv_port.setMaximum(10000)
        self.int_serv_port.setMinimum(2001)
        self.int_serv_port.setValue(8080)
        
        self.str_serv_addr = QLineEdit()  # Адрес сервера
        self.str_serv_addr.setText("192.168.1.1")
        self.str_serv_addr.setMaxLength(15)
    
        self.btn1_setup = QPushButton("Загрузить новый набор")  # Кнопка, отвечающая за загрузку файла с параметрами каналов
        self.btn2_setup = QPushButton("Загрузить новый набор")  
        self.btn_start_stop = QPushButton("Начать симуляцию")  # Позволяет включать и выключать поток симуляции каналов
        self.btn_start_stop.setDisabled(True)
        # self.btn3_sw_off = QPushButton("Отключить выходной сигнал")

        self.list1_on_off = QComboBox()
        self.list1_on_off.addItems(["Вкл", "Выкл"])
        self.list1_on_off.setCurrentIndex(0)

        self.list2_on_off = QComboBox()
        self.list2_on_off.addItems(["Вкл", "Выкл"])
        self.list2_on_off.setCurrentIndex(0)

        self.list3_on_off = QComboBox()
        self.list3_on_off.addItems(["Вкл", "Выкл"])
        self.list3_on_off.setCurrentIndex(0)

        self.list4_on_off = QComboBox()
        self.list4_on_off.addItems(["Вкл", "Выкл"])
        self.list4_on_off.setCurrentIndex(0)

        self.list1_in = QComboBox()
        self.list1_in.addItems(["in1", "in2", "in3", "in4"])
        self.list1_in.setCurrentIndex(0)

        self.list2_in = QComboBox()
        self.list2_in.addItems(["in1", "in2", "in3", "in4"])
        self.list2_in.setCurrentIndex(1)

        self.list3_in = QComboBox()
        self.list3_in.addItems(["in1", "in2", "in3", "in4"])
        self.list3_in.setCurrentIndex(2)

        self.list4_in = QComboBox()
        self.list4_in.addItems(["in1", "in2", "in3", "in4"])
        self.list4_in.setCurrentIndex(3)
        
        self.list1_out = QComboBox()
        self.list1_out.addItems(["out1", "out2", "out3", "out4"])
        self.list1_out.setCurrentIndex(1)
        
        self.list2_out = QComboBox()
        self.list2_out.addItems(["out1", "out2", "out3", "out4"])
        self.list2_out.setCurrentIndex(0)

        self.list3_out = QComboBox()
        self.list3_out.addItems(["out1", "out2", "out3", "out4"])
        self.list3_out.setCurrentIndex(3)

        self.list4_out = QComboBox()
        self.list4_out.addItems(["out1", "out2", "out3", "out4"])
        self.list4_out.setCurrentIndex(2)

        # Создание горизонтальных контейнеров
        # # Для первой пары модемов
        # hbox1_beams = QHBoxLayout()  # Задание контейнеров расположения для сдвига амплитуд
        # hbox1_beams.addStretch(1)
        # hbox1_beams.addWidget(self.dbl3_beams)
        # hbox1_beams.addWidget(lbl5_beams)

        # # Для второй пары модемов
        # hbox2_beams = QHBoxLayout()  # Задание контейнеров расположения для сдвига амплитуд
        # hbox2_beams.addStretch(1)
        # hbox2_beams.addWidget(self.dbl6_beams)
        # hbox2_beams.addWidget(lbl5_1_beams)

        # Для первой пары модемов
        hbox1_doppler = QHBoxLayout()   # Задание контейнеров для доплеровского сдвига и рассеивания
        hbox1_doppler.addWidget(self.dbl1_doppler)
        hbox1_doppler.addWidget(lbl3_doppler)

        hbox2_doppler = QHBoxLayout()
        hbox2_doppler.addWidget(self.dbl2_doppler)
        hbox2_doppler.addWidget(lbl4_doppler)

        # Для второй пары модемов
        hbox3_doppler = QHBoxLayout()   # Задание контейнеров для доплеровского сдвига и рассеивания
        hbox3_doppler.addWidget(self.dbl3_doppler)
        hbox3_doppler.addWidget(lbl3_1_doppler)

        hbox4_doppler = QHBoxLayout()
        hbox4_doppler.addWidget(self.dbl4_doppler)
        hbox4_doppler.addWidget(lbl4_1_doppler)

        # # Для первой пары модемов
        # hbox1_snr = QHBoxLayout()
        # hbox1_snr.addWidget(lbl1_snr)
        # hbox1_snr.addWidget(self.dbl1_snr)
        # hbox1_snr.addWidget(lbl2_snr)
        
        # hbox2_snr = QHBoxLayout()
        # hbox2_snr.addWidget(lbl18_snr)
        # hbox2_snr.addWidget(self.dbl2_snr)
        # hbox2_snr.addWidget(lbl2_snr)
        
        # hbox3_snr = QHBoxLayout()
        # hbox3_snr.addWidget(lbl19_snr)
        # hbox3_snr.addWidget(self.dbl3_snr)
        # hbox3_snr.addWidget(lbl2_snr)

        # # Для второй пары модемов
        # hbox4_snr = QHBoxLayout()
        # hbox4_snr.addWidget(lbl1_1_snr)
        # hbox4_snr.addWidget(self.dbl4_snr)
        # hbox4_snr.addWidget(lbl2_1_snr)
        
        # hbox5_snr = QHBoxLayout()
        # hbox5_snr.addWidget(lbl19_snr)
        # hbox5_snr.addWidget(self.dbl5_snr)
        # hbox5_snr.addWidget(lbl2_snr)
        
        # hbox6_snr = QHBoxLayout()
        # hbox6_snr.addWidget(lbl20_snr)
        # hbox6_snr.addWidget(self.dbl6_snr)
        # hbox6_snr.addWidget(lbl2_snr)
        
        # Контейнер для вывода сообщений
        hbox_term_output = QHBoxLayout()
        hbox_term_output.addWidget(self.txt1_term_output)
        
        # # Создание вертикальных контейнеров
        # # Для первой пары модемов
        # vbox1_beams = QVBoxLayout()
        # vbox1_beams.addStretch(1)
        # vbox1_beams.addLayout(hbox1_beams)

        # vbox2_beams = QVBoxLayout()
        # vbox2_beams.addStretch(1)
        # vbox2_beams.addWidget(lbl4_beams)
        # vbox2_beams.addSpacing(5)
        
        # # Для второй пары модемов
        # vbox3_beams = QVBoxLayout()
        # vbox3_beams.addStretch(1)
        # vbox3_beams.addLayout(hbox1_beams)

        # Контейнер справочного окна
        vbox_about = QVBoxLayout()
        vbox_about.addWidget(lbl1_about)
        vbox_about.addWidget(lbl2_about)
        vbox_about.addWidget(lbl3_about)
        vbox_about.addWidget(lbl4_about)
        vbox_about.setAlignment(Qt.AlignCenter)

        # Задание сеток
        # Для первой пары модемов
        grid1_beams = QGridLayout()  # Задание сетки для контейнера
        #  изменения амплитуд и вр. сдвига лучей
        grid1_beams.setSpacing(10)

        grid1_beams.addWidget(lbl1_beams, 0, 1)
        grid1_beams.addWidget(lbl2_beams, 1, 0)
        grid1_beams.addWidget(self.dbl1_beams, 1, 1)
        grid1_beams.addWidget(lbl3_beams, 2, 0)
        grid1_beams.addWidget(self.dbl2_beams, 2, 1)
        grid1_beams.addWidget(lbl4_beams, 3, 0)
        grid1_beams.addWidget(self.dbl3_beams, 3, 1)
        grid1_beams.addWidget(lbl5_beams, 3, 2)
        grid1_beams.setRowMinimumHeight(3, 40)

        # Для второй пары модемов
        grid2_beams = QGridLayout()  # Задание сетки для контейнера
        #  изменения амплитуд и вр. сдвига лучей
        grid2_beams.setSpacing(10)

        grid2_beams.addWidget(lbl1_1_beams, 0, 1)
        grid2_beams.addWidget(lbl2_1_beams, 1, 0)
        grid2_beams.addWidget(self.dbl4_beams, 1, 1)
        grid2_beams.addWidget(lbl3_1_beams, 2, 0)
        grid2_beams.addWidget(self.dbl5_beams, 2, 1)
        grid2_beams.addWidget(lbl4_1_beams, 3, 0)
        grid2_beams.addWidget(self.dbl6_beams, 3, 1)
        grid2_beams.addWidget(lbl5_1_beams, 3, 2)
        grid2_beams.setRowMinimumHeight(3, 40)

        # Для первой пары модемов
        grid1_doppler = QGridLayout()  # Задание сетки для Доплера
        grid1_doppler.setSpacing(10)
        grid1_doppler.addWidget(lbl1_doppler, 0, 0)
        grid1_doppler.addWidget(lbl2_doppler, 0, 1)
        grid1_doppler.addLayout(hbox1_doppler, 1, 0)
        grid1_doppler.addLayout(hbox2_doppler, 1, 1)

        # Для второй пары модемов
        grid2_doppler = QGridLayout()  # Задание сетки для Доплера
        grid2_doppler.setSpacing(10)
        grid2_doppler.addWidget(lbl1_1_doppler, 0, 0)
        grid2_doppler.addWidget(lbl2_1_doppler, 0, 1)
        grid2_doppler.addLayout(hbox3_doppler, 1, 0)
        grid2_doppler.addLayout(hbox4_doppler, 1, 1)
        
        # Для первой пары модемов
        grid1_snr = QGridLayout()  # Задание сетки для осш
        grid1_snr.addWidget(lbl1_snr, 0, 0)
        grid1_snr.addWidget(self.dbl1_snr, 0, 1)
        grid1_snr.addWidget(lbl2_snr, 0, 2)

        # Для второй пары модемов
        grid2_snr = QGridLayout()  # Задание сетки для осш
        grid2_snr.addWidget(lbl1_1_snr, 0, 0)
        grid2_snr.addWidget(self.dbl2_snr, 0, 1)
        grid2_snr.addWidget(lbl2_1_snr, 0, 2)

        # Для первой пары модемов
        grid1_commutation = QGridLayout()  # Задание горизонтального контейнера для коммутации входов и выходов
        grid1_commutation.addWidget(lbl1_commutation, 0, 0, 1, 2)
        grid1_commutation.addWidget(self.list1_on_off, 0, 2, 1, 2)
        grid1_commutation.addWidget(lbl2_commutation, 1, 0)
        grid1_commutation.addWidget(self.list1_in, 1, 1)
        grid1_commutation.addWidget(lbl3_commutation, 1, 2)
        grid1_commutation.addWidget(self.list1_out, 1, 3)
        grid1_commutation.addWidget(lbl4_commutation, 0, 4, 1, 2)
        grid1_commutation.addWidget(self.list2_on_off, 0, 6, 1, 2)
        grid1_commutation.addWidget(lbl5_commutation, 1, 4)
        grid1_commutation.addWidget(self.list2_in, 1, 5)
        grid1_commutation.addWidget(lbl6_commutation, 1, 6)
        grid1_commutation.addWidget(self.list2_out, 1, 7)

        # Для второй пары модемов
        grid2_commutation = QGridLayout()  # Задание горизонтального контейнера для коммутации входов и выходов
        grid2_commutation.addWidget(lbl7_commutation, 0, 0, 1, 2)
        grid2_commutation.addWidget(self.list3_on_off, 0, 2, 1, 2)
        grid2_commutation.addWidget(lbl8_commutation, 1, 0)
        grid2_commutation.addWidget(self.list3_in, 1, 1)
        grid2_commutation.addWidget(lbl9_commutation, 1, 2)
        grid2_commutation.addWidget(self.list3_out, 1, 3)
        grid2_commutation.addWidget(lbl10_commutation, 0, 4, 1, 2)
        grid2_commutation.addWidget(self.list4_on_off, 0, 6, 1, 2)
        grid2_commutation.addWidget(lbl11_commutation, 1, 4)
        grid2_commutation.addWidget(self.list4_in, 1, 5)
        grid2_commutation.addWidget(lbl12_commutation, 1, 6)
        grid2_commutation.addWidget(self.list4_out, 1, 7)

        # Создание групп
        # Для первой пары модемов
        gr_box1_beams = QGroupBox("Лучи")  # Задание группы изменения лучей
        gr_box1_beams.setLayout(grid1_beams)

        # Для второй пары модемов
        gr_box2_beams = QGroupBox("Лучи")  # Задание группы изменения лучей
        gr_box2_beams.setLayout(grid2_beams)

        # Для первой пары модемов
        gr_box1_doppler = QGroupBox("Доплер")  # Задание группы Доплера
        gr_box1_doppler.setLayout(grid1_doppler)

        # Для второй пары модемов
        gr_box2_doppler = QGroupBox("Доплер")  # Задание группы Доплера
        gr_box2_doppler.setLayout(grid2_doppler)
        
        # Для первой пары модемов
        gr_box1_snr = QGroupBox("Отношение сигнал/шум")
        gr_box1_snr.setLayout(grid1_snr)

        # Для первой пары модемов
        gr_box2_snr = QGroupBox("Отношение сигнал/шум")
        gr_box2_snr.setLayout(grid2_snr)
        
        # Для первой пары модемов
        gr_box1_vol = QGroupBox("Коммутация")
        gr_box1_vol.setLayout(grid1_commutation)

        # Для второй пары модемов
        gr_box2_vol = QGroupBox("Коммутация")
        gr_box2_vol.setLayout(grid2_commutation)

        # Для первой пары модемов
        grid_main1_fixed_freq_mode = QGridLayout() # Основная сетка режима работы фиксированной частоты
        grid_main1_fixed_freq_mode.addWidget(gr_box1_beams, 0, 0, 2, 1)
        grid_main1_fixed_freq_mode.addWidget(gr_box1_doppler, 0, 1)
        grid_main1_fixed_freq_mode.addWidget(gr_box1_snr, 1, 1)
        grid_main1_fixed_freq_mode.addWidget(gr_box1_vol, 2, 0, 1, 2)
        grid_main1_fixed_freq_mode.setSizeConstraint(QLayout.SetFixedSize)

        # Для второй пары модемов
        grid_main2_fixed_freq_mode = QGridLayout() # Основная сетка режима работы фиксированной частоты
        grid_main2_fixed_freq_mode.addWidget(gr_box2_beams, 0, 0, 2, 1)
        grid_main2_fixed_freq_mode.addWidget(gr_box2_doppler, 0, 1)
        grid_main2_fixed_freq_mode.addWidget(gr_box2_snr, 1, 1)
        grid_main2_fixed_freq_mode.addWidget(gr_box2_vol, 2, 0, 1, 2)
        grid_main2_fixed_freq_mode.setSizeConstraint(QLayout.SetFixedSize)

        # Для первой пары модемов
        grid_main1_freq_adapt_mode = QGridLayout() # Основная сетка режима работы адаптации по частоте
        grid_main1_freq_adapt_mode.addWidget(lbl1_freq_adapt_mode, 0, 0)
        grid_main1_freq_adapt_mode.addWidget(self.str_serv_addr, 0, 1)
        grid_main1_freq_adapt_mode.addWidget(lbl2_freq_adapt_mode, 1, 0)
        grid_main1_freq_adapt_mode.addWidget(self.int_serv_port, 1, 1)      
        grid_main1_freq_adapt_mode.addWidget(lbl3_freq_adapt_mode, 2, 0)
        grid_main1_freq_adapt_mode.addWidget(self.int1_m_addr, 2, 1)
        grid_main1_freq_adapt_mode.addWidget(lbl4_freq_adapt_mode, 3, 0)
        grid_main1_freq_adapt_mode.addWidget(self.int2_m_addr, 3, 1)
        grid_main1_freq_adapt_mode.addWidget(lbl7_freq_adapt_mode, 4, 0)
        grid_main1_freq_adapt_mode.addWidget(self.lbl8_freq_adapt_mode, 4, 1)
        grid_main1_freq_adapt_mode.addWidget(self.btn1_setup, 5, 0, 1, 2)
        grid_main1_freq_adapt_mode.setAlignment(Qt.AlignLeft)
        
        # Для второй пары модемов
        grid_main2_freq_adapt_mode = QGridLayout() # Основная сетка режима работы адаптации по частоте
        grid_main2_freq_adapt_mode.addWidget(lbl5_freq_adapt_mode, 0, 0, 1, 3)
        grid_main2_freq_adapt_mode.addWidget(self.int3_m_addr, 0, 3)
        grid_main2_freq_adapt_mode.addWidget(lbl6_freq_adapt_mode, 1, 0, 1, 3)
        grid_main2_freq_adapt_mode.addWidget(self.int4_m_addr, 1, 3)
        # grid_main2_freq_adapt_mode.addWidget(lbl9_freq_adapt_mode, 2, 0)
        # grid_main2_freq_adapt_mode.addWidget(self.lbl10_freq_adapt_mode, 2, 1)
        # grid_main2_freq_adapt_mode.addWidget(self.btn2_setup, 2, 2, 1, 2)
        grid_main2_freq_adapt_mode.setAlignment(Qt.AlignLeft)
        
        # Для первой пары модемов
        grid1_chosen_parameters = QGridLayout() # Сетка с выбранными установленными параметрами
        grid1_chosen_parameters.addWidget(lbl6_beams, 0, 0)
        grid1_chosen_parameters.addWidget(lbl7_beams, 1, 0)
        grid1_chosen_parameters.addWidget(self.lbl8_beams, 0, 1)
        grid1_chosen_parameters.addWidget(self.lbl9_beams, 1, 1)
        grid1_chosen_parameters.addWidget(lbl12_beams, 2, 0)
        grid1_chosen_parameters.addWidget(self.lbl13_beams, 2, 1)
        grid1_chosen_parameters.addWidget(lbl15_beams, 2, 3)

        grid1_chosen_parameters.addWidget(lbl5_doppler, 0, 4)
        grid1_chosen_parameters.addWidget(lbl6_doppler, 1, 4)
        grid1_chosen_parameters.addWidget(self.lbl7_doppler, 0, 5)
        grid1_chosen_parameters.addWidget(self.lbl8_doppler, 1, 5)
        grid1_chosen_parameters.addWidget(lbl9_doppler, 0, 6)
        grid1_chosen_parameters.addWidget(lbl10_doppler, 1, 6)

        grid1_chosen_parameters.addWidget(lbl3_snr, 2, 4)
        grid1_chosen_parameters.addWidget(self.lbl4_snr, 2, 5)
        grid1_chosen_parameters.addWidget(lbl5_snr, 2, 6)
        # grid1_chosen_parameters.addWidget(lbl6_snr, 3, 4)
        # grid1_chosen_parameters.addWidget(self.lbl7_snr, 3, 5)
        # grid1_chosen_parameters.addWidget(lbl8_snr, 3, 6)
        
        # Для второй пары модемов
        grid2_chosen_parameters = QGridLayout() # Сетка с выбранными установленными параметрами
        grid2_chosen_parameters.addWidget(lbl6_1_beams, 0, 1)
        grid2_chosen_parameters.addWidget(lbl7_1_beams, 1, 1)
        grid2_chosen_parameters.addWidget(self.lbl10_beams, 0, 2)
        grid2_chosen_parameters.addWidget(self.lbl11_beams, 1, 2)
        grid2_chosen_parameters.addWidget(lbl12_1_beams, 2, 1)
        grid2_chosen_parameters.addWidget(self.lbl14_beams, 2, 2)
        grid2_chosen_parameters.addWidget(lbl15_1_beams, 2, 3)

        grid2_chosen_parameters.addWidget(lbl5_1_doppler, 0, 4)
        grid2_chosen_parameters.addWidget(lbl6_1_doppler, 1, 4)
        grid2_chosen_parameters.addWidget(self.lbl7_1_doppler, 0, 5)
        grid2_chosen_parameters.addWidget(self.lbl8_1_doppler, 1, 5)
        grid2_chosen_parameters.addWidget(lbl9_1_doppler, 0, 6)
        grid2_chosen_parameters.addWidget(lbl10_1_doppler, 1, 6)

        grid2_chosen_parameters.addWidget(lbl3_1_snr, 2, 4)
        grid2_chosen_parameters.addWidget(self.lbl4_1_snr, 2, 5)
        grid2_chosen_parameters.addWidget(lbl5_1_snr, 2, 6)
        # grid2_chosen_parameters.addWidget(lbl6_snr, 3, 4)
        # grid2_chosen_parameters.addWidget(self.lbl7_snr, 3, 5)
        # grid2_chosen_parameters.addWidget(lbl8_snr, 3, 6)
        
        # Для первой пары модемов
        grid1_meas = QGridLayout() # Сетка с измеряемыми параметрами
        grid1_meas.addWidget(lbl6_snr, 0, 0)
        grid1_meas.addWidget(self.lbl7_snr, 0, 1)
        grid1_meas.addWidget(lbl8_snr, 0, 2)
        
        grid1_meas.addWidget(lbl9_snr, 0, 3)
        grid1_meas.addWidget(self.lbl10_snr, 0, 4)
        grid1_meas.addWidget(lbl11_snr, 0, 5)
        
        grid1_meas.addWidget(lbl1_rms, 1, 0)
        
        grid1_meas.addWidget(self.lbl2_rms, 1, 1)
        grid1_meas.addWidget(lbl4_rms, 1, 3)
        grid1_meas.addWidget(self.lbl5_rms, 1, 4)

        # Для второй пары модемов
        grid2_meas = QGridLayout() # Сетка с измеряемыми параметрами
        grid2_meas.addWidget(lbl12_snr, 0, 0)
        grid2_meas.addWidget(self.lbl13_snr, 0, 1)
        grid2_meas.addWidget(lbl14_snr, 0, 2)
        
        grid2_meas.addWidget(lbl15_snr, 0, 3)
        grid2_meas.addWidget(self.lbl16_snr, 0, 4)
        grid2_meas.addWidget(lbl17_snr, 0, 5)
        
        grid2_meas.addWidget(lbl1_1_rms, 1, 0)
        
        grid2_meas.addWidget(self.lbl3_rms, 1, 1)
        grid2_meas.addWidget(lbl4_1_rms, 1, 3)
        grid2_meas.addWidget(self.lbl6_rms, 1, 4)
        
        # Для первой пары модемов
        self.gr_box1_fixed_freq_mode = QGroupBox("Одиночная работа") # Задание группы режима фиксированной частоты
        self.gr_box1_fixed_freq_mode.setLayout(grid_main1_fixed_freq_mode)

        # Для второй пары модемов
        self.gr_box2_fixed_freq_mode = QGroupBox("Cовместная работа") # Задание группы режима фиксированной частоты
        self.gr_box2_fixed_freq_mode.setCheckable(True)
        self.gr_box2_fixed_freq_mode.setChecked(False)
        self.gr_box2_fixed_freq_mode.setLayout(grid_main2_fixed_freq_mode)

        hbox_fixed_freq_mode = QHBoxLayout()
        hbox_fixed_freq_mode.addWidget(self.gr_box1_fixed_freq_mode)
        # hbox_fixed_freq_mode.addWidget(self.gr_box2_fixed_freq_mode)

        # Для всех модемов
        self.gr_box3_fixed_freq_mode = QGroupBox("Режим фиксированной частоты") # Задание группы режима фиксированной частоты
        self.gr_box3_fixed_freq_mode.setCheckable(True)
        self.gr_box3_fixed_freq_mode.setChecked(False)
        self.gr_box3_fixed_freq_mode.setLayout(hbox_fixed_freq_mode)

        # Для первой пары модемов
        self.gr_box1_freq_adapt_mode = QGroupBox("Одиночная работа") # Задание группы режима адаптации по частоте
        self.gr_box1_freq_adapt_mode.setLayout(grid_main1_freq_adapt_mode)

        # Для второй пары модемов
        self.gr_box2_freq_adapt_mode = QGroupBox("Cовместная работа") # Задание группы режима адаптации по частоте
        self.gr_box2_freq_adapt_mode.setCheckable(True)
        self.gr_box2_freq_adapt_mode.setChecked(False)
        self.gr_box2_freq_adapt_mode.setLayout(grid_main2_freq_adapt_mode)

        hbox_freq_adapt_mode = QHBoxLayout()
        hbox_freq_adapt_mode.addWidget(self.gr_box1_freq_adapt_mode)
        hbox_freq_adapt_mode.addWidget(self.gr_box2_freq_adapt_mode)

        # Для всех модемов
        self.gr_box3_freq_adapt_mode = QGroupBox("Режим адаптации по частоте") # Задание группы режима адаптации по частоте
        self.gr_box3_freq_adapt_mode.setCheckable(True)
        self.gr_box3_freq_adapt_mode.setChecked(False)
        self.gr_box3_freq_adapt_mode.setLayout(hbox_freq_adapt_mode)

        self.gr_box1_chan_params = QGroupBox("Текущие выбранные параметры канала:") # Задание группы текущих выбранных параметров канала 1
        self.gr_box1_chan_params.setLayout(grid1_chosen_parameters)

        self.gr_box2_chan_params = QGroupBox("Текущие выбранные параметры канала 2:") # Задание группы текущих выбранных параметров канала 1
        self.gr_box2_chan_params.setLayout(grid2_chosen_parameters)
        
        self.gr_box1_meas = QGroupBox("Измерения канала:")
        self.gr_box1_meas.setLayout(grid1_meas)

        self.gr_box2_meas = QGroupBox("Измерения канала 2:")
        self.gr_box2_meas.setLayout(grid2_meas)
        
        self.gr_box7_term_output = QGroupBox("Сообщения:")
        self.gr_box7_term_output.setLayout(hbox_term_output)

        # Создание главной сетки окна
        grid_main = QGridLayout()
        grid_main.addWidget(self.gr_box3_fixed_freq_mode, 0, 0, 1, 2)
        grid_main.addWidget(self.gr_box3_freq_adapt_mode, 1, 0, 1, 2)
        grid_main.addWidget(self.gr_box1_chan_params, 2, 0)
        # grid_main.addWidget(self.gr_box2_chan_params, 2, 1 )
        grid_main.addWidget(self.gr_box1_meas, 3, 0)
        # grid_main.addWidget(self.gr_box2_meas, 3, 1)
        grid_main.addWidget(self.gr_box7_term_output, 0, 2, 5, 1)
        grid_main.addWidget(self.btn_start_stop, 4, 0, 1, 2)

        # vbox_mode = QVBoxLayout() # Задание контейнера режимов работы имитатора (фикс. частота, адаптация по частоте)
        # vbox_mode.addWidget(self.gr_box3_fixed_freq_mode)
        # vbox_mode.addWidget(self.gr_box3_freq_adapt_mode)
        # vbox_mode.addWidget(self.gr_box1_chan_params)
        # vbox_mode.addWidget(self.gr_box1_meas)
        # vbox_mode.addWidget(self.gr_box7_term_output)
        # vbox_mode.addWidget(self.btn_start_stop)
        # self.setLayout(vbox5_mode)
        
        self.about_window = QWidget()
        self.about_window.setWindowTitle("О программе Симулятор КВ канала")
        self.about_window.setWindowIcon(QIcon("simulator_logo1.png"))
        self.about_window.setWindowFlags(Qt.SubWindow)
        self.about_window.setLayout(vbox_about)
        self.about_window.setFixedSize(self.minimumSize())
        
        central_widget = QWidget()
        central_widget.setLayout(grid_main)

        self.setCentralWidget(central_widget)
        self.statusBar()

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        about = menubar.addAction("О программе")
        about.triggered.connect(self.show_about_window)
        
        self.statusBar().showMessage("Симулятор находится в режиме ожидания.")
        self.setWindowTitle('Симулятор КВ канала')
        self.setWindowIcon(QIcon("simulator_logo1.png"))
        self.setFixedSize(self.minimumSize())
        self.show()
            
    def show_about_window(self):
        self.about_window.show()
            
    def fixed_sel(self):
        if self.gr_box3_fixed_freq_mode.isChecked():                  
            self.btn_start_stop.setDisabled(False)
            self.btn_start_stop.setText("Начать симуляцию")
            self.gr_box3_freq_adapt_mode.setChecked(False)  # Для взаимоисключения одновременной работы в обоих режимах
        else:
            #self.btn2_start_stop.setDisabled(True)
            self.gr_box3_freq_adapt_mode.setChecked(True)  # Для взаимоисключения одновременной работы в обоих режимах
            
    def adapt_sel(self):
        if self.gr_box3_freq_adapt_mode.isChecked():
            
            self.btn_start_stop.setDisabled(False)
            self.btn_start_stop.setText("Начать симуляцию")
            self.gr_box3_fixed_freq_mode.setChecked(False)  # Для взаимоисключения одновременной работы в обоих режимах
        else:
            #self.btn2_start_stop.setDisabled(True)
            self.gr_box3_fixed_freq_mode.setChecked(True)  # Для взаимоисключения одновременной работы в обоих режимах
            
    def set_new_channels(self):
        new_chanels_csv_filename = QFileDialog.getOpenFileName(self, "Выберите файл c расширением .csv", "", "*.csv")[0]
        if new_chanels_csv_filename:
            print(f"Загружен файл с набором каналов: {new_chanels_csv_filename}:")
            with open(new_chanels_csv_filename, newline = '') as csvfile:
                csvreader = csv.reader(csvfile)
                for idx, row in enumerate(csvreader):
                    print(idx+1,": ",", ".join(row))
            print(' ')
            self.lbl8_freq_adapt_mode.setText(new_chanels_csv_filename.split("/")[-1])
            self.channels_csv_filename = new_chanels_csv_filename
                
    # def set_new_channels2(self):
    #     new_chanels_csv_filename = QFileDialog.getOpenFileName(self, "Выберите файл c расширением .csv", "", "*.csv")[0]
    #     if new_chanels_csv_filename:
    #         print(f"Загружен файл с набором каналов: {new_chanels_csv_filename}:")
    #         with open(new_chanels_csv_filename, newline = '') as csvfile:
    #             csvreader = csv.reader(csvfile)
    #             for idx, row in enumerate(csvreader):
    #                 print(idx+1,": ",", ".join(row))
    #         print(' ')
    #         self.lbl10_freq_adapt_mode.setText(new_chanels_csv_filename.split("/")[-1])
    #         self.channels_csv_filename2 = new_chanels_csv_filename
            
    def get_parameters_from_flow_graph1(self, obj):  # Передаём в выбранные параметры значения из потока симуляции
        if obj.ch1_flow_graph_is_running == obj.ch2_flow_graph_is_running == True:
            #  Передаём в выбранные параметры значения из потока симуляции
            self.lbl8_beams.setText(str(round(self.sim_handler1.get_ampl(0), 2)))  # Амплитуда первого луча

            self.lbl9_beams.setText(str(round(self.sim_handler1.get_ampl(1), 2)))  # Амплитуда второго луча
            
            self.lbl13_beams.setText(str(self.sim_handler1.get_tau()*1000))  # Задержка второго луча относительно первого
                        
            self.lbl7_doppler.setText(str(round(self.sim_handler1.get_dop_freq_shift(), 2)))  # Доплеровский сдвиг частоты
                        
            # Передаём в выбранные параметры установленные значения доплеровского уширения и отношения сигнал-шум
            self.lbl8_doppler.setText(str(round(self.sim_handler1.get_dop_ir(), 2)))  # Доплеровское уширение (рассеивание)
            self.lbl4_snr.setText(str(round(self.sim_handler1.snr, 2)))  # Отношение сигнал-шум
            
            snr1 = round(self.sim_handler1.get_ch1_snr(), 2)
            snr2 = round(self.sim_handler1.get_ch2_snr(), 2)
            rms1 = round(self.sim_handler1.get_ch1_rms(), 2)
            rms2 = round(self.sim_handler1.get_ch2_rms(), 2)
            
            self.lbl7_snr.setText(str(snr1))
            self.lbl10_snr.setText(str(snr2))
            self.lbl2_rms.setText(str(rms1))
            self.lbl5_rms.setText(str(rms2))
            
            if rms1 or rms2:
                if rms1 > 0.2 or rms2 > 0.2:
                    self.statusBar().showMessage("Внимание, превышен допустимый уровень входного сигнала!")
                elif rms1 < 0.2 and rms2 < 0.2:
                    self.statusBar().showMessage("Симулятор работает, параметры в норме")
            else:
                self.statusBar().showMessage("Входной сигнал отсутствует")
                self.lbl7_snr.setText("-")
                self.lbl10_snr.setText("-")
        else:
            #  Для выбранных параметров
            self.lbl8_beams.setText("-")  # Амплитуда первого луча
            self.lbl9_beams.setText("-")  # Амплитуда второго луча
            self.lbl13_beams.setText("-")  # Задержка второго луча относительно первого
            self.lbl7_doppler.setText("-")  # Доплеровский сдвиг частоты
            self.lbl8_doppler.setText("-")  # Доплеровское уширение (рассеивание)
            self.lbl4_snr.setText("-")  # Отношение сигнал-шум
            
            #  Для измеряемых параметров
            self.lbl2_rms.setText("-")
            self.lbl5_rms.setText("-")
#             self.lbl5_rms.setText("-")
            self.lbl7_snr.setText("-")
            self.lbl10_snr.setText("-")
            
            self.statusBar().showMessage("Симулятор находится в режиме ожидания.")

    def get_parameters_from_flow_graph2(self, obj):  # Передаём в выбранные параметры значения из потока симуляции
        if obj.ch1_flow_graph_is_running == obj.ch2_flow_graph_is_running == True:
            #  Передаём в выбранные параметры значения из потока симуляции
            self.lbl10_beams.setText(str(round(self.sim_handler2.get_ampl(0), 2)))  # Амплитуда первого луча

            self.lbl11_beams.setText(str(round(self.sim_handler2.get_ampl(1), 2)))  # Амплитуда второго луча
            
            self.lbl14_beams.setText(str(self.sim_handler2.get_tau()*1000))  # Задержка второго луча относительно первого
                        
            self.lbl7_1_doppler.setText(str(round(self.sim_handler2.get_dop_freq_shift(), 2)))  # Доплеровский сдвиг частоты
                        
            # Передаём в выбранные параметры установленные значения доплеровского уширения и отношения сигнал-шум
            self.lbl8_1_doppler.setText(str(round(self.sim_handler2.get_dop_ir(), 2)))  # Доплеровское уширение (рассеивание)
            self.lbl4_1_snr.setText(str(round(self.sim_handler2.snr, 2)))  # Отношение сигнал-шум
            
            snr1 = round(self.sim_handler2.get_ch1_snr(), 2)
            snr2 = round(self.sim_handler2.get_ch2_snr(), 2)
            rms1 = round(self.sim_handler2.get_ch1_rms(), 2)
            rms2 = round(self.sim_handler2.get_ch2_rms(), 2)
            
            self.lbl13_snr.setText(str(snr1))
            self.lbl16_snr.setText(str(snr2))
            self.lbl3_rms.setText(str(rms1))
            self.lbl6_rms.setText(str(rms2))
            
            if rms1 or rms2:
                if rms1 > 0.2 or rms2 > 0.2:
                    self.statusBar().showMessage("Внимание, превышен допустимый уровень входного сигнала!")
                elif rms1 < 0.2 and rms2 < 0.2:
                    self.statusBar().showMessage("Симулятор работает, параметры в норме")
            else:
                self.statusBar().showMessage("Входной сигнал отсутствует")
                self.lbl13_snr.setText("-")
                self.lbl16_snr.setText("-")
        else:
            #  Для выбранных параметров
            self.lbl10_beams.setText("-")  # Амплитуда первого луча
            self.lbl11_beams.setText("-")  # Амплитуда второго луча
            self.lbl14_beams.setText("-")  # Задержка второго луча относительно первого
            self.lbl7_1_doppler.setText("-")  # Доплеровский сдвиг частоты
            self.lbl8_1_doppler.setText("-")  # Доплеровское уширение (рассеивание)
            self.lbl4_1_snr.setText("-")  # Отношение сигнал-шум
            
            #  Для измеряемых параметров
            self.lbl3_rms.setText("-")
            self.lbl6_rms.setText("-")
#             self.lbl5_rms.setText("-")
            self.lbl13_snr.setText("-")
            self.lbl16_snr.setText("-")
            
            self.statusBar().showMessage("Симулятор находится в режиме ожидания.")        
        
    # Для одиночной работы
    def start_sim_in_fixed_mode1(self):  
        # Присваиваем экземпляру self.sim_handler параметры из редактируемых полей 
             
        self.sim_handler1.ampl1 = round(self.dbl1_beams.value(), 2)  # Амплитуда первого луча
        self.sim_handler1.ampl2 = round(self.dbl2_beams.value(), 2)  # Амплитуда второго луча
        self.sim_handler1.tau = round(self.dbl3_beams.value(), 2)/1000  # Задержка второго луча относительно первого
        self.sim_handler1.dop_shift = round(self.dbl1_doppler.value(), 2)  # Доплеровский сдвиг частоты
        self.sim_handler1.dop_fd = round(self.dbl2_doppler.value(), 2)  # Доплеровское уширение (рассеивание)
        self.sim_handler1.snr = round(self.dbl1_snr.value(), 2)  # Отношение сигнал-шум
        
        self.sim_handler1.on_off_out1 = not self.list1_on_off.currentIndex()
        self.sim_handler1.on_off_out2 = not self.list2_on_off.currentIndex()
        
        self.sim_handler1.in1_sel = self.list1_in.currentIndex()
        self.sim_handler1.out1_sel = self.list1_out.currentIndex()
        self.sim_handler1.in2_sel = self.list2_in.currentIndex()
        self.sim_handler1.out2_sel = self.list2_out.currentIndex()
        self.sim_handler1.ch1_en_silence_noise = 0
        self.sim_handler1.ch2_en_silence_noise = 0
        
        self.sim_handler1.ch1_start_sim()  # Запуск симуляции канала
        self.sim_handler1.ch2_start_sim()

        # Производим операции необходимые для измерения 
        timer_callback = functools.partial(self.get_parameters_from_flow_graph1, obj = self.sim_handler1)
        self.timer1 = QTimer()
        self.timer1.setSingleShot(False)
        self.timer1.timeout.connect(timer_callback)  # Заполняем поля выбранных и измеренных параметров)
        self.timer1.start(100)
        
        self.statusBar().showMessage("Поток выполнения запущен в режиме фиксированной частоты.")
        self.btn_start_stop.setText("Остановить симуляцию")
        self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
        self.gr_box3_freq_adapt_mode.setEnabled(False)

    # Для совместной работы
    def start_sim_in_fixed_mode2(self):  
        # Присваиваем экземпляру self.sim_handler параметры из редактируемых полей 
             
        self.sim_handler2.ampl1 = round(self.dbl4_beams.value(), 2)  # Амплитуда первого луча
        self.sim_handler2.ampl2 = round(self.dbl5_beams.value(), 2)  # Амплитуда второго луча
        self.sim_handler2.tau = round(self.dbl6_beams.value(), 2)/1000  # Задержка второго луча относительно первого
        self.sim_handler2.dop_shift = round(self.dbl3_doppler.value(), 2)  # Доплеровский сдвиг частоты
        self.sim_handler2.dop_fd = round(self.dbl4_doppler.value(), 2)  # Доплеровское уширение (рассеивание)
        self.sim_handler2.snr = round(self.dbl2_snr.value(), 2)  # Отношение сигнал-шум
        
        self.sim_handler2.on_off_out1 = not self.list3_on_off.currentIndex()
        self.sim_handler2.on_off_out2 = not self.list4_on_off.currentIndex()

        self.sim_handler2.in1_sel = self.list3_in.currentIndex()
        self.sim_handler2.out1_sel = self.list3_out.currentIndex()
        self.sim_handler2.in2_sel = self.list4_in.currentIndex()
        self.sim_handler2.out2_sel = self.list4_out.currentIndex()
        self.sim_handler2.ch1_en_silence_noise = 0
        self.sim_handler2.ch2_en_silence_noise = 0
        
        self.sim_handler2.ch1_start_sim()  # Запуск симуляции канала
        self.sim_handler2.ch2_start_sim()

        # Производим операции необходимые для измерения 
        timer_callback = functools.partial(self.get_parameters_from_flow_graph2, obj = self.sim_handler2)
        self.timer2 = QTimer()
        self.timer2.setSingleShot(False)
        self.timer2.timeout.connect(timer_callback)  # Заполняем поля выбранных и измеренных параметров)
        self.timer2.start(100)
           
    def setup_sim_in_adapt_mode(self):
        self.adapt_mode.teamwork = self.teamwork
        with open("address.cfg", "w") as address_file:
            address_file.write(f"{self.int1_m_addr.value()} {self.int2_m_addr.value()}")
        self.adapt_mode.host = self.str_serv_addr.text()
        self.adapt_mode.port = self.int_serv_port.value()
        self.adapt_mode.channels_csv_filename = self.channels_csv_filename

        # if self.teamwork:
        #     with open("address.cfg", "a") as address_file:
        #         address_file.write(f" {self.int3_m_addr.value()} {self.int4_m_addr.value()}")
        #     self.adapt_mode.channels_csv_filename2 = self.channels_csv_filename2
        
    def check_if_csv_file_with_channels_exists(self, channels_csv_filename):
        try: 
            if not os.path.exists(channels_csv_filename):
                raise FileNotFoundError
            # elif not os.path.exists(channels_csv_filename2) and self.teamwork:
            #     raise FileNotFoundError
            else:
                return True
        except FileNotFoundError as err:
            print(f"Файл(ы) не существует(ют), пожалуйста выберите существующий(ие) файл(ы) с параметрами каналов\n")
            return False
            pass
        
    def start_stop_button_handler(self):
        if self.gr_box3_fixed_freq_mode.isChecked():  # Если выбран режим фиксированной частоты
            if self.sim_handler1.ch1_flow_graph_is_running and self.sim_handler1.ch2_flow_graph_is_running:
                self.sim_handler1.ch1_stop_sim()  # Остановка симуляции в режиме фиксированной частоты
                self.sim_handler1.ch2_stop_sim()
                if self.teamwork:  # Если выбран режим совместной работы
                    self.sim_handler2.ch1_stop_sim()
                    self.sim_handler2.ch2_stop_sim()
                print("Поток выполнения остановлен\n")
                self.statusBar().showMessage("Поток выполнения остановлен")
                self.btn_start_stop.setText("Начать симуляцию")
                self.gr_box3_fixed_freq_mode.setEnabled(True)  # Разблокировывает редактироватие параметров после остановки симуляции
                self.gr_box3_freq_adapt_mode.setEnabled(True)
            elif not (self.sim_handler1.ch1_flow_graph_is_running and self.sim_handler1.ch2_flow_graph_is_running):
                self.start_sim_in_fixed_mode1()
                if self.gr_box2_fixed_freq_mode.isChecked():  # Если выбран режим совместной работы
                    self.teamwork = True
                    self.start_sim_in_fixed_mode2()
                else:
                    self.teamwork = False
                print("Поток выполнения запущен в режиме фиксированной частоты\n")
                self.statusBar().showMessage("Поток выполнения запущен в режиме фиксированной частоты.")
                self.btn_start_stop.setText("Остановить симуляцию")
                self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                self.gr_box3_freq_adapt_mode.setEnabled(False)
        elif self.gr_box3_freq_adapt_mode.isChecked():  # Если выбран режим адаптации по частоте
            if self.gr_box2_freq_adapt_mode.isChecked():
                self.teamwork = True
            else:
                self.teamwork = False
            if self.adapt_mode.is_alive():
                if not self.adapt_mode.server_is_running:  # Если сервер приостановлен после предыдущего нажатия на кнопку, тогда возобновляем режим адаптации
                    if not self.check_if_csv_file_with_channels_exists(self.channels_csv_filename):
                        return
                    self.setup_sim_in_adapt_mode()  # Записываем изменившиеся параметры из пользовательского интерфейса, если таковые имеются
                    self.adapt_mode.stop_server_flag = False
                    self.statusBar().showMessage("Поток выполнения запущен в режиме адаптации по частоте")
                    self.btn_start_stop.setText("Остановить симуляцию")
                    self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                    self.gr_box3_freq_adapt_mode.setEnabled(False)
                else:  # Если нет, то ставим сервер на паузу
                    self.adapt_mode.stop_server_flag = True
                    print("Поток выполнения остановлен\n")
                    self.statusBar().showMessage("Поток выполнения остановлен")
                    self.btn_start_stop.setText("Начать симуляцию")
                    self.gr_box3_fixed_freq_mode.setEnabled(True)  # Разблокировывает редактироватие параметров после остановки симуляции
                    self.gr_box3_freq_adapt_mode.setEnabled(True)
            else:
                if not self.check_if_csv_file_with_channels_exists(self.channels_csv_filename):
                    return
                
                self.setup_sim_in_adapt_mode()
                self.adapt_mode.start()
        
                # # Производим операции необходимые для измерения 
                # timer_callback = functools.partial(self.get_parameters_from_flow_graph1, obj = self.adapt_mode.sim_handler1)
                # self.timer3 = QTimer()
                # self.timer3.setSingleShot(False)
                # self.timer3.timeout.connect(timer_callback)  # Заполняем поля выбранных и измеренных параметров)
                # self.timer3.start(100)
                
                self.statusBar().showMessage("Поток выполнения запущен в режиме адаптации по частоте")
                self.btn_start_stop.setText("Остановить симуляцию")
                self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                self.gr_box3_freq_adapt_mode.setEnabled(False)

    def switch_off_on_out(self):
        self.btn3_sw_off.setText("Включить выходной сигнал")
        self.sim_handler1.off_out = True

    def signals(self):               
        self.gr_box3_fixed_freq_mode.toggled.connect(self.fixed_sel)  # Обработка сигнала выбора режима фикс. частоты
        self.btn1_setup.clicked.connect(self.set_new_channels)  # Обработка сигнала нажатия на кнопку для загрузки новых параметров
        # self.btn2_setup.clicked.connect(self.set_new_channels2)  # Обработка сигнала нажатия на кнопку для загрузки новых параметров
        self.gr_box3_freq_adapt_mode.toggled.connect(self.adapt_sel)  # Обработка сигнала выбора режима адапт. частоты
        #self.gr_box4_freq_adapt_mode.toggled.connect(self.adapt_sel())  # Обработка сигнала выбора режима адаптации по частоте
        self.btn_start_stop.clicked.connect(self.start_stop_button_handler)  # Обработка сигнала нажатия на кнопку старт-стоп
    
    def append_log(self, text):
        """Append text to the QTextEdit."""
#         self.txt1_term_output.append(text)
        cursor = self.txt1_term_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.txt1_term_output.setTextCursor(cursor)
        self.txt1_term_output.ensureCursorVisible()
    
class OutputLogger(QObject):
    emit_write = pyqtSignal(str)
    
    def write(self, text):
        self.emit_write.emit(str(text))
