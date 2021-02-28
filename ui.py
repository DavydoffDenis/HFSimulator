'''
Created on Jul 2, 2020

@author: user
'''
import parameters_handler
from PyQt5.QtWidgets import (QWidget, QMainWindow, QTextEdit, QApplication,
                             QPushButton, QAction, qApp, QLineEdit, QFileDialog,
                             QGroupBox, QLabel, QDoubleSpinBox, QSpinBox,
                             QHBoxLayout, QVBoxLayout, QGridLayout, QLayout)
from PyQt5.QtGui import QIcon, QTextCursor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal

import simulation
import functools
import epoll_server
import sys
import csv

class UserInterface(QMainWindow):
    '''
    Интерфейс пользователя на базе класса QMainWindow
    '''
    
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.sim_t = simulation.simulation()  # Создаем экземпляр класса потока выполнения симуляции канала
        self.sim_handler = parameters_handler.Parameters(self.sim_t)  # Создаем экземпляр класса обслуживающего поток симуляции  
#         self.adapt_mode = AsyncServer.ServerThread(self.sim_handler, self.tcp_host, self.tcp_port)  # Создаем экземпляр класса сервера для режима адапт. частоты
        self.adapt_mode = epoll_server.ServerHandler(self.sim_handler)
        
    def init_ui(self):
        lbl1_beams = QLabel("Амплитуда")
        lbl2_beams = QLabel("Первый луч:")
        lbl3_beams = QLabel("Второй луч:")
        lbl4_beams = QLabel("Временной сдвиг:")
        lbl5_beams = QLabel("мс")
        
        lbl6_beams = QLabel("Амплитуда первого луча:")
        lbl7_beams = QLabel("Амплитуда второго луча:")
        self.lbl8_beams = QLabel("-")
        self.lbl9_beams = QLabel("-")
        lbl10_beams = QLabel("Временной сдвиг между лучами:")
        self.lbl11_beams = QLabel("-")
        lbl12_beams = QLabel("мс")

        lbl1_doppler = QLabel("Доплеровский сдвиг:")
        lbl2_doppler = QLabel("Доп. рассеивание:")
        lbl3_doppler = QLabel("Гц")
        lbl4_doppler = QLabel("Гц")
        
        lbl5_doppler = QLabel("Доплеровский сдвиг:")
        lbl6_doppler = QLabel("Доплеровское  уширение:")
        self.lbl7_doppler = QLabel("-")
        self.lbl8_doppler = QLabel("-")
        lbl9_doppler = QLabel("Гц")
        lbl10_doppler = QLabel("Гц")

        lbl1_snr = QLabel("Отношение сигнал/шум")
        lbl2_snr = QLabel("дБ")
        
        lbl3_snr = QLabel("ОСШ установленное:")
        self.lbl4_snr = QLabel("-")
        lbl5_snr = QLabel("дБ")
        
        lbl6_snr = QLabel("ОСШ измеренное 1 канал:")
        self.lbl7_snr = QLabel("-")
        lbl8_snr = QLabel("дБ")
        
        lbl6_1_snr = QLabel("ОСШ измеренное 2 канал:")
        self.lbl7_1_snr = QLabel("-")
        lbl8_1_snr = QLabel("дБ")
        
        lbl9_snr = QLabel("Множитель сигнала на выходе 1:")
        lbl10_snr = QLabel("Множитель сигнала на выходе 2:")
        #self.lbl12_snr = QLabel("ОСШ измеренный")
        
        lbl1_rms = QLabel("Среднеквадратическое отклонение первого луча измеренное:")
        self.lbl2_rms = QLabel("-")
        lbl3_rms = QLabel("Среднеквадратическое отклонение второго луча измеренное:")
        self.lbl4_rms = QLabel("-")
#         self.lbl5_rms = QLabel("Симулятор находится в режиме ожидания.")

        lbl13_freq_adapt_mode = QLabel("Адрес сервера:")
        lbl14_freq_adapt_mode = QLabel("Номер порта:")
        lbl15_freq_adapt_mode = QLabel("Адрес модема подкл. к первому вх. зв. карты:")        
        lbl16_freq_adapt_mode = QLabel("Адрес модема подкл. ко второму вх. зв. карты:")
        lbl17_freq_adapt_mode = QLabel("Набор каналов:")
        self.lbl18_freq_adapt_mode = QLabel("params.csv")
        self.channels_csv_filename = "params.csv"
        
        lbl17_about = QLabel()
        pixmap = QPixmap("polet.png")
        lbl17_about.setPixmap(pixmap)
        lbl18_about = QLabel("Версия: 1.69")
        lbl19_about = QLabel("Авторы проекта: Алексей Львов, Денис Давыдов")
        lbl20_about = QLabel('АО "НПП "Полет", 2019-2021 г.')
        
        self.txt1_term_output = QTextEdit()  # Поле вывода сообщений симулятора
        self.txt1_term_output.setReadOnly(True)
        self.txt1_term_output.setMinimumHeight(150)
        
        sys.stdout = OutputLogger(emit_write = self.append_log)
        sys.stderr = OutputLogger(emit_write = self.append_log)
        
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

        self.dbl4_doppler = QDoubleSpinBox()  # Доплеровоский сдвиг лучей в формате с плавающей точкой
        self.dbl4_doppler.setMaximum(75)
        self.dbl4_doppler.setMinimum(-75)
        self.dbl4_doppler.setSingleStep(1)

        self.dbl5_doppler = QDoubleSpinBox()  # Доплеровское рассеивание (уширение)
        self.dbl5_doppler.setMaximum(30)
        self.dbl5_doppler.setMinimum(0)
        self.dbl5_doppler.setValue(1.0)
        self.dbl5_doppler.setSingleStep(0.1)

        self.dbl6_snr = QDoubleSpinBox()  # Отношение сигнал-шум
        self.dbl6_snr.setMaximum(40)
        self.dbl6_snr.setMinimum(-20)
        self.dbl6_snr.setValue(10)
        self.dbl6_snr.setSingleStep(1)
        
        self.dbl7_snr = QDoubleSpinBox()  # Множитель сигнала на выходе 1
        self.dbl7_snr.setMaximum(1.0)
        self.dbl7_snr.setMinimum(0)
        self.dbl7_snr.setValue(1.0)
        self.dbl7_snr.setSingleStep(1.0)

        self.dbl8_snr = QDoubleSpinBox()  # Множитель сигнала на выходе 2
        self.dbl8_snr.setMaximum(1.0)
        self.dbl8_snr.setMinimum(0)
        self.dbl8_snr.setValue(1.0)
        self.dbl8_snr.setSingleStep(1.0)
        
        self.int1_m_addr = QSpinBox()  # Адрес первого модема
        self.int1_m_addr.setValue(12)
        
        self.int2_m_addr = QSpinBox()  # Адрес второго модема
        self.int2_m_addr.setValue(14)
        
        self.int3_serv_port = QSpinBox()  # Порт на котором слушает сервер
        self.int3_serv_port.setMaximum(10000)
        self.int3_serv_port.setMinimum(2001)
        self.int3_serv_port.setValue(8080)
        
        self.str1_serv_addr = QLineEdit()  # Адрес сервера
        self.str1_serv_addr.setText("localhost")
        self.str1_serv_addr.setMaxLength(11)
        
        self.btn1_setup = QPushButton("Загрузить новый набор частотных каналов")  # Кнопка, отвечающая за загрузку файла с параметрами каналов
        self.btn2_start_stop = QPushButton("Запустить симуляцию канала")  # Позволяет включать и выключать поток симуляции канала 
        self.btn2_start_stop.setDisabled(True)
        # self.btn3_sw_off = QPushButton("Отключить выходной сигнал")
        
        hbox1_beams = QHBoxLayout()  # Задание контейнеров расположения для сдвига амплитуд
        hbox1_beams.addStretch(1)
        hbox1_beams.addWidget(self.dbl3_beams)
        hbox1_beams.addWidget(lbl5_beams)

        hbox2_doppler = QHBoxLayout()   # Задание контейнеров для доплеровского сдвига и рассеивания
        hbox2_doppler.addWidget(self.dbl4_doppler)
        hbox2_doppler.addWidget(lbl3_doppler)

        hbox3_doppler = QHBoxLayout()
        hbox3_doppler.addWidget(self.dbl5_doppler)
        hbox3_doppler.addWidget(lbl4_doppler)

        hbox4_snr = QHBoxLayout()
        hbox4_snr.addWidget(lbl1_snr)
        hbox4_snr.addWidget(self.dbl6_snr)
        hbox4_snr.addWidget(lbl2_snr)
        
        hbox5_snr = QHBoxLayout()
        hbox5_snr.addWidget(lbl9_snr)
        hbox5_snr.addWidget(self.dbl7_snr)
        hbox5_snr.addWidget(lbl2_snr)
        
        hbox6_snr = QHBoxLayout()
        hbox6_snr.addWidget(lbl10_snr)
        hbox6_snr.addWidget(self.dbl8_snr)
        hbox6_snr.addWidget(lbl2_snr)
        
        hbox7_term_output = QHBoxLayout()
        hbox7_term_output.addWidget(self.txt1_term_output)
        
        vbox1_beams = QVBoxLayout()
        vbox1_beams.addStretch(1)
        vbox1_beams.addLayout(hbox1_beams)

        vbox2_beams = QVBoxLayout()
        vbox2_beams.addStretch(1)
        vbox2_beams.addWidget(lbl4_beams)
        vbox2_beams.addSpacing(5)
        
        vbox_about = QVBoxLayout()
        vbox_about.addWidget(lbl17_about)
        vbox_about.addWidget(lbl18_about)
        vbox_about.addWidget(lbl19_about)
        vbox_about.addWidget(lbl20_about)
        vbox_about.setAlignment(Qt.AlignCenter)

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

        grid2_doppler = QGridLayout()  # Задание сетки для контейнера Доплера
        grid2_doppler.setSpacing(10)
        grid2_doppler.addWidget(lbl1_doppler, 0, 0)
        grid2_doppler.addWidget(lbl2_doppler, 0, 1)
        grid2_doppler.addLayout(hbox2_doppler, 1, 0)
        grid2_doppler.addLayout(hbox3_doppler, 1, 1)
        
        grid3_snr = QGridLayout()  # Задание сетки для осш
        grid3_snr.addWidget(lbl1_snr, 0, 0)
        grid3_snr.addWidget(self.dbl6_snr, 0, 1)
        grid3_snr.addWidget(lbl2_snr, 0, 2)

        hbox7_vol = QHBoxLayout()  # Задание горизонтального контейнера для регулировки выходного сигнала
        hbox7_vol.addWidget(lbl9_snr)
        hbox7_vol.addWidget(self.dbl7_snr)
        hbox7_vol.addWidget(lbl10_snr)
        hbox7_vol.addWidget(self.dbl8_snr)

        gr_box1_beams = QGroupBox("Лучи")  # Задание группы изменения лучей
        gr_box1_beams.setLayout(grid1_beams)

        gr_box2_doppler = QGroupBox("Доплер")  # Задание группы Доплера
        gr_box2_doppler.setLayout(grid2_doppler)
        
        gr_box3_snr = QGroupBox("Отношение сигнал/шум")
        gr_box3_snr.setLayout(grid3_snr)
        
        gr_box4_vol = QGroupBox("Регулировка выходного сигнала")
        gr_box4_vol.setLayout(hbox7_vol)

        grid_main_fixed_freq_mode = QGridLayout() # Основная сетка режима работы фиксированной частоты
        grid_main_fixed_freq_mode.addWidget(gr_box1_beams, 0, 0, 2, 1)
        grid_main_fixed_freq_mode.addWidget(gr_box2_doppler, 0, 1)
        grid_main_fixed_freq_mode.addWidget(gr_box3_snr, 1, 1)
        grid_main_fixed_freq_mode.addWidget(gr_box4_vol, 2, 0, 1, 2)
        grid_main_fixed_freq_mode.setSizeConstraint(QLayout.SetFixedSize)

        grid_main_freq_adapt_mode = QGridLayout() # Основная сетка режима работы адаптации по частоте
        grid_main_freq_adapt_mode.addWidget(lbl13_freq_adapt_mode, 0, 0)
        grid_main_freq_adapt_mode.addWidget(self.str1_serv_addr, 0, 1)
        grid_main_freq_adapt_mode.addWidget(lbl14_freq_adapt_mode, 1, 0)
        grid_main_freq_adapt_mode.addWidget(self.int3_serv_port, 1, 1)      
        grid_main_freq_adapt_mode.addWidget(lbl15_freq_adapt_mode, 0, 2)
        grid_main_freq_adapt_mode.addWidget(self.int1_m_addr, 0, 3)
        grid_main_freq_adapt_mode.addWidget(lbl16_freq_adapt_mode, 1, 2)
        grid_main_freq_adapt_mode.addWidget(self.int2_m_addr, 1, 3)
        grid_main_freq_adapt_mode.addWidget(lbl17_freq_adapt_mode, 2, 0)
        grid_main_freq_adapt_mode.addWidget(self.lbl18_freq_adapt_mode, 2, 1)
        grid_main_freq_adapt_mode.addWidget(self.btn1_setup, 2, 2, 1, 2)
        grid_main_freq_adapt_mode.setAlignment(Qt.AlignLeft)
        
        grid_chosen_parameters = QGridLayout() # Сетка с выбранными установленными параметрами
        grid_chosen_parameters.addWidget(lbl6_beams, 0, 0)
        grid_chosen_parameters.addWidget(lbl7_beams, 1, 0)
        grid_chosen_parameters.addWidget(self.lbl8_beams, 0, 1)
        grid_chosen_parameters.addWidget(self.lbl9_beams, 1, 1)
        grid_chosen_parameters.addWidget(lbl10_beams, 2, 0)
        grid_chosen_parameters.addWidget(self.lbl11_beams, 2, 1)
        grid_chosen_parameters.addWidget(lbl12_beams, 2, 3)
        
        grid_chosen_parameters.addWidget(lbl5_doppler, 0, 4)
        grid_chosen_parameters.addWidget(lbl6_doppler, 1, 4)
        grid_chosen_parameters.addWidget(self.lbl7_doppler, 0, 5)
        grid_chosen_parameters.addWidget(self.lbl8_doppler, 1, 5)
        grid_chosen_parameters.addWidget(lbl9_doppler, 0, 6)
        grid_chosen_parameters.addWidget(lbl10_doppler, 1, 6)

        grid_chosen_parameters.addWidget(lbl3_snr, 2, 4)
        grid_chosen_parameters.addWidget(self.lbl4_snr, 2, 5)
        grid_chosen_parameters.addWidget(lbl5_snr, 2, 6)
        grid_chosen_parameters.addWidget(lbl6_snr, 3, 4)
        grid_chosen_parameters.addWidget(self.lbl7_snr, 3, 5)
        grid_chosen_parameters.addWidget(lbl8_snr, 3, 6)
        
        grid_meas = QGridLayout() # Сетка с измеряемыми параметрами
        grid_meas.addWidget(lbl6_snr, 0, 0)
        grid_meas.addWidget(self.lbl7_snr, 0, 1)
        grid_meas.addWidget(lbl8_snr, 0, 2)
        
        grid_meas.addWidget(lbl6_1_snr, 1, 0)
        grid_meas.addWidget(self.lbl7_1_snr, 1, 1)
        grid_meas.addWidget(lbl8_1_snr, 1, 2)
        
        grid_meas.addWidget(lbl1_rms, 2, 0)
        
        grid_meas.addWidget(self.lbl2_rms, 2, 1)
        grid_meas.addWidget(lbl3_rms, 3, 0)
        grid_meas.addWidget(self.lbl4_rms, 3, 1)
        
        self.gr_box3_fixed_freq_mode = QGroupBox("Режим фиксированной частоты") # Задание группы режима фиксированной частоты
        self.gr_box3_fixed_freq_mode.setCheckable(True)
        self.gr_box3_fixed_freq_mode.setChecked(False)
        self.gr_box3_fixed_freq_mode.setLayout(grid_main_fixed_freq_mode)

        self.gr_box4_freq_adapt_mode = QGroupBox("Режим адаптации по частоте") # Задание группы режима адаптации по частоте
        self.gr_box4_freq_adapt_mode.setCheckable(True)
        self.gr_box4_freq_adapt_mode.setChecked(False)
        self.gr_box4_freq_adapt_mode.setLayout(grid_main_freq_adapt_mode)
        
        self.gr_box5_chan_params = QGroupBox("Текущие выбранные параметры канала:") # Задание группы текущих выбранных параметров канала
        self.gr_box5_chan_params.setLayout(grid_chosen_parameters)
        
        self.gr_box6_meas = QGroupBox("Измерения:")
        self.gr_box6_meas.setLayout(grid_meas)
        
        self.gr_box7_term_output = QGroupBox("Сообщения:")
        self.gr_box7_term_output.setLayout(hbox7_term_output)

        vbox5_mode = QVBoxLayout() # Задание контейнера режимов работы имитатора (фикс. частота, адаптация по частоте)
        vbox5_mode.addWidget(self.gr_box3_fixed_freq_mode)
        vbox5_mode.addWidget(self.gr_box4_freq_adapt_mode)
        vbox5_mode.addWidget(self.gr_box5_chan_params)
        vbox5_mode.addWidget(self.gr_box6_meas)
        vbox5_mode.addWidget(self.gr_box7_term_output)
        vbox5_mode.addWidget(self.btn2_start_stop)
        # self.setLayout(vbox5_mode)
        
        self.about_window = QWidget()
        self.about_window.setWindowTitle("О программе Симулятор КВ канала")
        self.about_window.setWindowIcon(QIcon("simulator_logo1.png"))
        self.about_window.setWindowFlags(Qt.SubWindow)
        self.about_window.setLayout(vbox_about)
        self.about_window.setFixedSize(self.minimumSize())
        
        central_widget = QWidget()
        central_widget.setLayout(vbox5_mode)

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
            
                    
            self.btn2_start_stop.setDisabled(False)
            self.btn2_start_stop.setText("Запустить симуляцию в режиме фиксированной частоты")
            self.gr_box4_freq_adapt_mode.setChecked(False)  # Для взаимоисключения одновременной работы в обоих режимах
        else:
            #self.btn2_start_stop.setDisabled(True)
            self.gr_box4_freq_adapt_mode.setChecked(True)  # Для взаимоисключения одновременной работы в обоих режимах
            
    def adapt_sel(self):
        
        if self.gr_box4_freq_adapt_mode.isChecked():
            
            self.btn2_start_stop.setDisabled(False)
            self.btn2_start_stop.setText("Запустить симуляцию в режиме адаптации по частоте")
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
            self.lbl18_freq_adapt_mode.setText(new_chanels_csv_filename.split("/")[-1])
            self.channels_csv_filename = new_chanels_csv_filename
            
    def get_parameters_from_flow_graph(self, obj):  # Передаём в выбранные параметры значения из потока симуляции
        if obj.flow_graph_is_running == True:
            #  Передаём в выбранные параметры значения из потока симуляции
    #         self.lbl8_beams.setText(str(round(self.sim_handler.get_ampl()[0][0], 2)))  # Амплитуда первого луча
            self.lbl8_beams.setText(str(round(obj.sim_t.get_ampl()[0][0], 2)))  # Амплитуда первого луча
            
    #         self.lbl9_beams.setText(str(round(self.sim_handler.get_ampl()[0][1], 2)))  # Амплитуда второго луча
            self.lbl9_beams.setText(str(round(obj.sim_t.get_ampl()[0][1], 2)))  # Амплитуда второго луча
            
    #         self.lbl11_beams.setText(str(self.sim_handler.get_tau()*1000))  # Задержка второго луча относительно первого
            self.lbl11_beams.setText(str(obj.sim_t.get_tau()*1000))  # Задержка второго луча относительно первого
            
    #         self.lbl7_doppler.setText(str(round(self.sim_handler.get_dop_freq_shift(), 2)))  # Доплеровский сдвиг частоты
            self.lbl7_doppler.setText(str(round(obj.sim_t.get_freqShift(), 2)))  # Доплеровский сдвиг частоты
            
            # Передаём в выбранные параметры установленные значения доплеровского уширения и отношения сигнал-шум
            self.lbl8_doppler.setText(str(round(obj.sim_t.get_fd(), 2)))  # Доплеровское уширение (рассеивание)
            self.lbl4_snr.setText(str(round(obj.snr, 2)))  # Отношение сигнал-шум
            
            #  Извлекаем данные, которые кладутся в измеренные параметры
            snr = obj.sim_t.get_snrVecOut()
            rms1 = round(obj.sim_t.get_outSigRMSVec()[0], 2)
            rms2 = round(obj.sim_t.get_outSigRMSVec()[1], 2)
            
            self.lbl7_snr.setText(str(round(snr[2], 2)))
            self.lbl7_1_snr.setText(str(round(snr[3], 2)))
            self.lbl2_rms.setText(str(rms1))
            self.lbl4_rms.setText(str(rms2))
            
            if rms1 or rms2:
                if rms1 > 0.2 or rms2 > 0.2:
                    self.statusBar().showMessage("Внимание, превышен допустимый уровень входного сигнала!")
                elif rms1 < 0.2 and rms2 < 0.2:
                    self.statusBar().showMessage("Симулятор работает, параметры в норме")
            else:
                self.statusBar().showMessage("Входной сигнал отсутствует")
                self.lbl7_snr.setText("-")
                self.lbl7_1_snr.setText("-")
        else:
            #  Для выбранных параметров
            self.lbl8_beams.setText("-")  # Амплитуда первого луча
            self.lbl9_beams.setText("-")  # Амплитуда второго луча
            self.lbl11_beams.setText("-")  # Задержка второго луча относительно первого
            self.lbl7_doppler.setText("-")  # Доплеровский сдвиг частоты
            self.lbl8_doppler.setText("-")  # Доплеровское уширение (рассеивание)
            self.lbl4_snr.setText("-")  # Отношение сигнал-шум
            
            #  Для измеряемых параметров
            self.lbl2_rms.setText("-")
            self.lbl4_rms.setText("-")
#             self.lbl5_rms.setText("-")
            self.lbl7_snr.setText("-")
            self.lbl7_1_snr.setText("-")
            
            self.statusBar().showMessage("Симулятор находится в режиме ожидания.")
        
    def start_sim_in_fixed_mode(self):  
        # Присваиваем экземпляру self.sim_handler параметры из редактируемых полей 
             
        self.sim_handler.ampl1 = round(self.dbl1_beams.value(), 2)  # Амплитуда первого луча
        self.sim_handler.ampl2 = round(self.dbl2_beams.value(), 2)  # Амплитуда второго луча
        self.sim_handler.tau = round(self.dbl3_beams.value(), 2)/1000  # Задержка второго луча относительно первого
        self.sim_handler.dop_shift = round(self.dbl4_doppler.value(), 2)  # Доплеровский сдвиг частоты
        self.sim_handler.dop_fd = round(self.dbl5_doppler.value(), 2)  # Доплеровское уширение (рассеивание)
        self.sim_handler.snr = round(self.dbl6_snr.value(), 2)  # Отношение сигнал-шум
        
        self.sim_handler.on_off_out1 = self.dbl7_snr.value()
        self.sim_handler.on_off_out2 = self.dbl8_snr.value()
        
        self.sim_handler.start_sim()  # Запуск симуляции канала
        
        # Производим операции необходимые для измерения 
        timer_callback = functools.partial(self.get_parameters_from_flow_graph, obj = self.sim_handler)
        self.timer = QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(timer_callback)  # Заполняем поля выбранных и измеренных параметров)
        self.timer.start(100)
        
        self.statusBar().showMessage("Поток выполнения запущен в режиме фиксированной частоты.")
        self.btn2_start_stop.setText("Остановить симуляцию канала")
        self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
        self.gr_box4_freq_adapt_mode.setEnabled(False)
    
#     def preemptive_start_for_b(self):
#         # Функция запускает симулятор на 1-м канале до установления соединения
#         # Присваиваем экземпляру self.sim_handler выбранные параметры 
#              
#         self.sim_handler.ampl1 = 1.0  # Амплитуда первого луча
#         self.sim_handler.ampl2 = 1.0  # Амплитуда второго луча
#         self.sim_handler.tau = 1.0 * 1e-3  # Задержка второго луча относительно первого
#         self.sim_handler.dop_shift = 0.0  # Доплеровский сдвиг частоты
#         self.sim_handler.dop_fd = 0.0  # Доплеровское уширение (рассеивание)
#         self.sim_handler.snr = 40.0  # Отношение сигнал-шум
#         
#         self.sim_handler.on_off_out1 = 1.0
#         self.sim_handler.on_off_out2 = 1.0
#         
#         self.sim_handler.start_sim()  # Запуск симуляции канала
#         
#         # Производим операции необходимые для измерения 
#         self.timer = QTimer()
#         self.timer.setSingleShot(False)
#         self.timer.timeout.connect(self.update_meas)
#         self.timer.start(100)
    
    def setup_sim_in_adapt_mode(self):
        with open("address.cfg", "w") as address_file:
            address_file.write(f"{self.int1_m_addr.value()} {self.int2_m_addr.value()}")
        self.adapt_mode.host = self.str1_serv_addr.text()
        self.adapt_mode.port = self.int3_serv_port.value()
        self.adapt_mode.channels_csv_filename = self.channels_csv_filename
        
    def start_stop_button_handler(self):
        if self.gr_box3_fixed_freq_mode.isChecked():  # Если выбран режим фиксированной частоты
            if self.sim_handler.flow_graph_is_running:
                self.sim_handler.stop_sim()  # Остановка симуляции в режиме фиксированной частоты
                print("Поток выполнения остановлен\n")
                self.statusBar().showMessage("Поток выполнения остановлен")
                self.btn2_start_stop.setText("Запустить симуляцию канала")
                self.gr_box3_fixed_freq_mode.setEnabled(True)  # Разблокировывает редактироватие параметров после остановки симуляции
                self.gr_box4_freq_adapt_mode.setEnabled(True)
            elif not self.sim_handler.flow_graph_is_running:
                self.start_sim_in_fixed_mode()
                print("Поток выполнения запущен в режиме фиксированной частоты\n")
                self.statusBar().showMessage("Поток выполнения запущен в режиме фиксированной частоты.")
                self.btn2_start_stop.setText("Остановить симуляцию канала")
                self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                self.gr_box4_freq_adapt_mode.setEnabled(False)
        elif self.gr_box4_freq_adapt_mode.isChecked():  # Если выбран режим адаптации по частоте
            if self.adapt_mode.is_alive():
                if not self.adapt_mode.server_is_running:  # Если сервер приостановлен после предыдущего нажатия на кнопку, тогда возобновляем режим адаптации
                    self.setup_sim_in_adapt_mode()  # Записываем изменившиеся параметры из пользовательского интерфейса, если таковые имеются
                    self.adapt_mode.stop_server_flag = False
                    self.statusBar().showMessage("Поток выполнения запущен в режиме адаптации по частоте")
                    self.btn2_start_stop.setText("Остановить симуляцию канала")
                    self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                    self.gr_box4_freq_adapt_mode.setEnabled(False)
                else:  # Если нет, то ставим сервер на паузу
                    self.adapt_mode.stop_server_flag = True
                    print("Поток выполнения остановлен\n")
                    self.statusBar().showMessage("Поток выполнения остановлен")
                    self.btn2_start_stop.setText("Запустить симуляцию канала")
                    self.gr_box3_fixed_freq_mode.setEnabled(True)  # Разблокировывает редактироватие параметров после остановки симуляции
                    self.gr_box4_freq_adapt_mode.setEnabled(True)
            else:
                self.setup_sim_in_adapt_mode()
                self.adapt_mode.start()
        
                # Производим операции необходимые для измерения 
                timer_callback = functools.partial(self.get_parameters_from_flow_graph, obj = self.adapt_mode.sim_handler)
                self.timer = QTimer()
                self.timer.setSingleShot(False)
                self.timer.timeout.connect(timer_callback)  # Заполняем поля выбранных и измеренных параметров)
                self.timer.start(100)
                
                self.statusBar().showMessage("Поток выполнения запущен в режиме адаптации по частоте")
                self.btn2_start_stop.setText("Остановить симуляцию канала")
                self.gr_box3_fixed_freq_mode.setEnabled(False)  # Блокирует редактирование параметров во время симуляции
                self.gr_box4_freq_adapt_mode.setEnabled(False)

    def switch_off_on_out(self):
        self.btn3_sw_off.setText("Включить выходной сигнал")
        self.sim_handler.off_out = True
        
    '''        
        if self.sim_handler:
            if self.sim_handler.flow_graph_is_running:
                if self.gr_box3_fixed_freq_mode.isChecked():
                    self.sim_handler.stop_sim()  # Остановка симуляции в режиме фиксированной частоты
                elif self.gr_box4_freq_adapt_mode.isChecked():
                    self.adapt_t.stop()
                self.statusBar().showMessage("Поток выполнения остановлен.")
                self.btn2_start_stop.setText("Запустить симуляцию канала")
                self.lbl7_snr.setText(" 00.00")
                self.gr_box3_fixed_freq_mode.setEnabled(True)  # Разблокировывает редактироватие параметров после остановки симуляции
                self.gr_box4_freq_adapt_mode.setEnabled(True)
            elif not self.sim_handler.flow_graph_is_running:
                if self.gr_box3_fixed_freq_mode.isChecked():                       
                    self.start_sim_in_fixed_mode()
        else:                     
            if self.gr_box3_fixed_freq_mode.isChecked():  # Стаарт симуляции в режиме фиксированной частоты
                self.sim_handler = parameters_handler.Parameters()  # Создаем экземпляр класса обслуживающего поток симуляции
                self.start_sim_in_fixed_mode()
                
            elif self.gr_box4_freq_adapt_mode.isChecked():  # Старт симуляции в режиме адаптации по частоте
                self.adapt_t = async_server.ServerThread("localhost", self.tcp_port)  # Создаем поток для адаптации по частоте
                self.adapt_t.start()
                self.statusBar().showMessage("Адаптация по частоте включена...")
    '''
    def signals(self):               
        self.gr_box3_fixed_freq_mode.toggled.connect(self.fixed_sel)  # Обработка сигнала выбора режима фикс. частоты
        self.btn1_setup.clicked.connect(self.set_new_channels)  # Обработка сигнала нажатия на кнопку для загрузки новых параметров
        self.gr_box4_freq_adapt_mode.toggled.connect(self.adapt_sel)  # Обработка сигнала выбора режима адапт. частоты
        #self.gr_box4_freq_adapt_mode.toggled.connect(self.adapt_sel())  # Обработка сигнала выбора режима адаптации по частоте
        self.btn2_start_stop.clicked.connect(self.start_stop_button_handler)  # Обработка сигнала нажатия на кнопку старт-стоп
        
#         self.btn1_setup.clicked.connect(self.set_new_channels)  # Обработка сигнала нажатия на кнопку для загрузки новых параметров
        
        #self.btn3_sw_off.clicked.connect(self.switch_off_out)
    
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
        
        
