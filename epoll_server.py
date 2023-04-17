'''
Created on Nov 20, 2020

@author: denis
'''

import socket
import csv
from threading import Thread
import select
import time
import datetime

class ServerHandler(Thread):
    def __init__(self, sim_handler1, sim_handler2):
        super().__init__(daemon = True)
        self.sim_handler1 = sim_handler1
        self.sim_handler2 = sim_handler2
        self.host = None
        self.port = None
        self.channels_csv_filename1 = None
        self.channels_csv_filename2 = None
        self.teamwork = None
        self.current_modem = None
        self.current_working_pair1 = [0,0]
        self.current_working_pair2 = [0,0]

        self.modem_1_RX_ch_num = -1  # Старый номер приемного канала модема подключенного к первому входу звуковой карты
        self.modem_1_TX_ch_num = -1  # Старый номер передающего канала модема подключенного к первому входу звуковой карты
        self.modem_2_RX_ch_num = -1  # Старый номер приемного канала модема подключенного ко второму входу звуковой карты
        self.modem_2_TX_ch_num = -1  # Старый номер передающего канала модема подключенного ко второму входу звуковой карты
        self.modem_3_RX_ch_num = -1  # Старый номер приемного канала модема подключенного к третьему входу звуковой карты
        self.modem_3_TX_ch_num = -1  # Старый номер передающего канала модема подключенного к третьему входу звуковой карты
        self.modem_4_RX_ch_num = -1  # Старый номер приемного канала модема подключенного ко четвёртому входу звуковой карты
        # self.modem_4_TX_ch_num = -1  # Старый номер передающего канала модема подключенного ко четвёртому входу звуковой карты
        
        self.new_modem_1_RX_ch_num = None  # Новый номер приемного канала модема подключенного к первому входу звуковой карты
        self.new_modem_1_TX_ch_num = None  # Новый номер передающего канала модема подключенного к первому входу звуковой карты
        self.new_modem_2_RX_ch_num = None  # Новый номер приемного канала модема подключенного ко второму входу звуковой карты
        self.new_modem_2_TX_ch_num = None  # Новый номер передающего канала модема подключенного ко второму входу звуковой карты
        self.new_modem_3_RX_ch_num = None  # Новый номер приемного канала модема подключенного к третьему входу звуковой карты
        self.new_modem_3_TX_ch_num = None  # Новый номер передающего канала модема подключенного к третьему входу звуковой карты
        self.new_modem_4_RX_ch_num = None  # Новый номер приемного канала модема подключенного ко четвёртому входу звуковой карты
        # self.new_modem_4_TX_ch_num = None  # Новый номер передающего канала модема подключенного ко четвёртому входу звуковой карты

        # self.ch1_noise_already_on = False
        # self.ch2_noise_already_on = False
        # self.ch3_noise_already_on = False
        # self.ch4_noise_already_on = False
        
        self.server_is_running = None  
        self.stop_server_flag = None
        
        self.data_to_read = None
        self.data_to_send = None
        
        self.t1 = None  # Время включения канала
        self.t2 = None  # Время выключения канала
        
        self.conn_map = dict()  # Служит для связи создаваемых объектов соединений с файловыми дескрипторами (числами), адресами модемов и каналами на прием и передачу
        
    def start_sim(self, sim_handler, channel_num, restart_channels, new_commutation = (0,1,1,0)):  
        f = open(self.channels_csv_filename1, "r")
        i = 0  # Номер строки в csv файле
        for r in csv.reader(f):
            i += 1
            if i == channel_num + 1:
                floats = map(float, r)
                self.ampl1, self.ampl2, self.tau, self.dop_shift, self.dop_fd, self.snr = floats
        if any(self.ampl_mult):
            print(f"Параметры симуляции:\n a1 - {self.ampl1}, a2 - {self.ampl2}, tau - {self.tau}, dop_shift - {self.dop_shift}, dop_fd - {self.dop_fd}, snr - {self.snr}")
            print("Процесс симуляции запущен...")
        sim_handler.ch1_restart = restart_channels[0]
        sim_handler.ch2_restart = restart_channels[1]
        if sim_handler.ch1_flow_graph_is_running and restart_channels[0] == True:
            sim_handler.ch1_stop_sim()  # Останавливаем симуляцию для переконфигурирования симулятора
        if sim_handler.ch2_flow_graph_is_running and restart_channels[1] == True:
            sim_handler.ch2_stop_sim()  # Останавливаем симуляцию для переконфигурирования симулятора
        sim_handler.ampl1 = self.ampl1  # Амплитуда первого луча
        sim_handler.ampl2 = self.ampl2  # Амплитуда второго луча
        sim_handler.tau = self.tau * 0.001  # Задержка второго луча относительно первого
        sim_handler.dop_shift = self.dop_shift  # Доплеровский сдвиг частоты
        sim_handler.dop_fd = self.dop_fd  # Доплеровское уширение (рассеивание)
        sim_handler.snr = self.snr  # Отношение сигнал-шум
        sim_handler.on_off_out1 = self.ampl_mult[0]
        sim_handler.on_off_out2 = self.ampl_mult[1]
        sim_handler.ch1_en_silence_noise = 0
        sim_handler.ch2_en_silence_noise = 0

        if restart_channels[0] == restart_channels[1] == True:
            sim_handler.in1_sel = new_commutation[0]
            sim_handler.out1_sel = new_commutation[1]
            sim_handler.in2_sel = new_commutation[2]
            sim_handler.out2_sel = new_commutation[3]
            sim_handler.ch1_start_sim()  # Запуск симуляции канала
            sim_handler.ch2_start_sim()
        elif restart_channels[0] == True:
            sim_handler.in1_sel = new_commutation[0]
            sim_handler.out1_sel = new_commutation[1]
            sim_handler.ch1_start_sim()
        elif restart_channels[1] == True:
            sim_handler.in2_sel = new_commutation[2]
            sim_handler.out2_sel = new_commutation[3]
            sim_handler.ch2_start_sim()

    def read_data_handler(self, fileno):
        if self.t1:
            self.t2 = datetime.datetime.now()
            dt = self.t2 - self.t1
            self.t1 = 0
            self.t2 = 0
            print(f"Время до перестройки {dt.seconds}.{dt.microseconds} c.")
        f = open('address.cfg', 'r')
        print("\n")
        if self.teamwork:
            addr_1_cfg, addr_2_cfg, addr_3_cfg, addr_4_cfg = map(int, f.read().split())
            modem_address = self.data_to_read[0]
            if modem_address == addr_1_cfg:
                self.current_modem = 1
                self.new_modem_1_RX_ch_num = self.data_to_read[2]
                self.new_modem_1_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от первого модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            elif modem_address == addr_2_cfg:
                self.current_modem = 2
                self.new_modem_2_RX_ch_num = self.data_to_read[2]
                self.new_modem_2_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от второго модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            elif modem_address == addr_3_cfg:
                self.current_modem = 3
                self.new_modem_3_RX_ch_num = self.data_to_read[2]
                self.new_modem_3_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от третьего модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            elif modem_address == addr_4_cfg:
                self.current_modem = 4
                self.new_modem_4_RX_ch_num = self.data_to_read[2]
                # self.new_modem_4_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от четвёртого модема: адрес - {modem_address}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            else:
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Адрес модема: {modem_address} не допустим, ожидание...\n")
                return 
        else:
            addr_1_cfg, addr_2_cfg = map(int, f.read().split())
            modem_address = self.data_to_read[0]
            if modem_address == addr_1_cfg:
                self.current_modem = 1
                self.new_modem_1_RX_ch_num = self.data_to_read[2]
                self.new_modem_1_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от первого модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            elif modem_address == addr_2_cfg:
                self.current_modem = 2
                self.new_modem_2_RX_ch_num = self.data_to_read[2]
                self.new_modem_2_TX_ch_num = self.data_to_read[1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение от второго модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            else:
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Адрес модема: {modem_address} не допустим, ожидание...\n")
                return 

        if self.teamwork:
            if None in [self.new_modem_1_TX_ch_num, self.new_modem_1_RX_ch_num, \
                        self.new_modem_2_TX_ch_num, self.new_modem_2_RX_ch_num, \
                        self.new_modem_3_TX_ch_num, self.new_modem_3_RX_ch_num, \
                        self.new_modem_4_RX_ch_num]:
                if None in [self.new_modem_1_TX_ch_num, self.new_modem_1_RX_ch_num]:
                    print(f'Не получены номера каналов первого модема, ожидание...')
                if None in [self.new_modem_2_TX_ch_num, self.new_modem_2_RX_ch_num]:
                    print(f'Не получены номера каналов второго модема, ожидание...')
                if None in [self.new_modem_3_TX_ch_num, self.new_modem_3_RX_ch_num] and self.teamwork:
                    print(f'Не получены номера каналов третьего модема, ожидание...')
                # elif None in [self.new_modem_4_TX_ch_num, self.new_modem_4_RX_ch_num] and self.teamwork:
                if None in [self.new_modem_4_RX_ch_num] and self.teamwork:
                    print(f'Не получены номера каналов четвёртого модема, ожидание...')
                return
            
            if self.current_modem == 1:
                if self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                   self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                   self.modem_1_TX_ch_num == self.modem_3_RX_ch_num ==\
                   self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                    # Повторное включение того же канала,
                    # первый и третий модемы слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_1_TX_ch_num
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_1_TX_ch_num == self.modem_3_RX_ch_num:
                    # Повторное включение первого канала, новый второй канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Выбранный новый второй канал: {channel_number}, первый канал совпадает с действующим")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем второй канал с новыми параметрами, первый канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (0,1)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
                
                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                # Повторное включение второго канала, новый первый канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
            
                    print(f"Выбранный новый первый канал: {channel_number}, второй канал совпадает с действующим")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем первый канал с новыми параметрами, второй канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (1,0)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)    

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num:
                # Включение нового частотного канала,
                # оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Новый выбранный канал: {channel_number}")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    new_commutation = (0,2,2,0)
                    restart_channels = (1,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.modem_1_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение того же канала,
                # Третий модем слышит первого, первый не слышит третий
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Третий модем слышит первого, первый не слышит третий")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_2_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch2_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (0,2,2,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch2_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                # Повторное включение того же канала,
                # первый модем слышит третьего, третий не слышит первого
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Первый модем слышит третьего, третий не слышит первого")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch1_noise_already_on:
                    #     self.ampl_mult = [0, 1]
                    #     self.en_noise = [1, 0]
                    #     restart_channels = (1,0)
                    #     new_commutation = (0,2,2,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch1_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num:
                # Включение нового частотного канала,
                # третий модем слышит первого, первый не слышит третьего.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    restart_channels = (1,0)
                    print(f"Выбранный канал: {channel_number}")
                    print("Третий модем слышит первого, первый не слышит третьего")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch2_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch2_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num:
                # первый модем слышит третьего, третий не слышит первого
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    self.ampl_mult = [0, 1]
                    # self.en_noise = [1, 0]
                    restart_channels = (0,1)
                    print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                    print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                    print(f"Выбранный канал: {channel_number}")
                    print("Первый модем слышит третьего, третий не слышит первого")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch1_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch1_noise_already_on = True
                    # else:
                    #     restart_channels = (0,1)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_4_RX_ch_num ==\
                     self.modem_1_TX_ch_num == self.modem_4_RX_ch_num:
                # Повторное включение того же канала,
                # Четвёртый модем слышит первого, первый не слышит четвёртый.
                    self.current_working_pair2 = [1,4]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    # self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Четвёртый модем слышит первого, первый не слышит четвёртый")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch4_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (0,3,3,0)
                    #     self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    #     self.ch4_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_4_RX_ch_num:
                # Включение нового частотного канала,
                # Четвёртый модем слышит первого, первый не слышит четвёртый.
                    self.current_working_pair2 = [1,4]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    restart_channels = (1,0)
                    print(f"Выбранный канал: {channel_number}")
                    print("Четвёртый модем слышит первого, первый не слышит четвёртый")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    # if not self.ch4_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch4_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    new_commutation = (1,3,3,1)
                    self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    # self.ch3_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                else:
                    # Первый модем никого не слышит и первого модема никто не слышит
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num

                    channel_number = 1
                    self.ampl_mult = [0, 0]
                    # self.en_noise = [1, 1]
                    print(f"Первый модем никого не слышит и первого модема никто не слышит: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}")
                    print("Процесс симуляции остановлен!")
                    if 1 in self.current_working_pair1:
                        self.sim_handler1.ch1_stop_sim()
                        self.sim_handler1.ch2_stop_sim()
                        self.current_working_pair1 = [0,0]
                    if 1 in self.current_working_pair2:
                        self.sim_handler2.ch1_stop_sim()
                        self.sim_handler2.ch2_stop_sim()
                        self.current_working_pair2 = [0,0]

                    # if self.ch1_noise_already_on == self.ch2_noise_already_on == False:
                    #     restart_channels = (1,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch1_noise_already_on == False:
                    #     restart_channels = (1,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch2_noise_already_on == False:
                    #     restart_channels = (0,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # self.ch1_noise_already_on = True
                    # self.ch2_noise_already_on = True

                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.current_modem == 2:
                if self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение того же канала,
                # Второй и третий модемы оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_2_TX_ch_num
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Второй и третий модемы оба слышат друг друга - симметричный канал.")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение первого канала, новый второй канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num

                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Выбранный новый второй канал: {channel_number}, первый канал совпадает с действующим")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем второй канал с новыми параметрами, первый канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (0,1)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение второго канала, новый первый канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный новый первый канал: {channel_number}, второй канал совпадает с действующим")
                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем первый канал с новыми параметрами, второй канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (1,0)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num:
                # Включение нового частотного канала,
                # оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    
                    print(f"Новый выбранный канал: {channel_number}")
                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    new_commutation = (1,2,2,1)
                    restart_channels = (1,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение того же канала,
                # Третий модем слышит второго, второй не слышит третий
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Третий модем слышит второго, второй не слышит третий")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_2_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch2_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (1,2,2,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch2_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение того же канала,
                # Второй модем слышит третьего, третий не слышит второго
                    self.current_working_pair1 = [2,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Второй модем слышит третьего, третий не слышит второго")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch1_noise_already_on:
                    #     self.ampl_mult = [0, 1]
                    #     self.en_noise = [1, 0]
                    #     restart_channels = (1,0)
                    #     new_commutation = (1,2,2,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch1_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num:
                # Включение нового частотного канала,
                # Третий модем слышит второго, второй не слышит третий
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    
                    print(f"Выбранный канал: {channel_number}")
                    print("Третий модем слышит второго, второй не слышит третий")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch2_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch2_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    restart_channels = (1,0)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num:
                # Второй модем слышит третьего, третий не слышит второго
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    self.ampl_mult = [0, 1]
                    # self.en_noise = [1, 0]
                    print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                    print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                    print(f"Выбранный канал: {channel_number}")
                    print("Второй модем слышит третьего, третий не слышит второго")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch1_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch1_noise_already_on = True
                    # else:
                    #     restart_channels = (0,1)
                    restart_channels = (0,1)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_4_RX_ch_num ==\
                self.modem_2_TX_ch_num == self.modem_4_RX_ch_num:
                # Повторное включение того же канала,
                # Четвёртый слышит второго, второй не слышит четвёртого.
                    self.current_working_pair1 = [2,4]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Четвёртый слышит второго, второй не слышит четвёртого.")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch4_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (1,3,3,1)
                    #     outs_on_off = (1,0)
                    #     self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation, outs_on_off)
                    #     self.ch4_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_4_RX_ch_num:
                # Включение нового частотного канала,
                # втрой слышит первого, первый не слышит второй.
                    self.current_working_pair1 = [2,4]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    
                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    
                    print(f"Выбранный канал: {channel_number}")
                    print("Второй слышит первого, первый не слышит второй")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    # if not self.ch4_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch4_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    restart_channels = (1,0)
                    new_commutation = (1,3,3,1)
            
                    self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    # self.ch3_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                else:
                    # Второй модем никого не слышит и второго модема никто не слышит
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                    channel_number = 1
                    self.ampl_mult = [0, 0]
                    # self.en_noise = [1, 1]
                    print(f"Первый модем никого не слышит и первого модема никто не слышит: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}")
                    print("Процесс симуляции остановлен!")
                    if 2 in self.current_working_pair1:
                        self.sim_handler1.ch1_stop_sim()
                        self.sim_handler1.ch2_stop_sim()
                        self.current_working_pair1 = [0,0]
                    if 2 in self.current_working_pair2:
                        self.sim_handler2.ch1_stop_sim()
                        self.sim_handler2.ch2_stop_sim()
                        self.current_working_pair2 = [0,0]

                    # if self.ch1_noise_already_on == self.ch2_noise_already_on == False:
                    #     restart_channels = (1,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch1_noise_already_on == False:
                    #     restart_channels = (1,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch2_noise_already_on == False:
                    #     restart_channels = (0,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # self.ch1_noise_already_on = True
                    # self.ch2_noise_already_on = True

                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.current_modem == 3:
                if self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                   self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                   self.modem_1_TX_ch_num == self.modem_3_RX_ch_num ==\
                   self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                    # Повторное включение того же канала,
                    # первый и третий модемы слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_1_TX_ch_num
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_1_TX_ch_num == self.modem_3_RX_ch_num:
                    # Повторное включение первого канала, новый второй канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Выбранный новый второй канал: {channel_number}, первый канал совпадает с действующим")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем второй канал с новыми параметрами, первый канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (0,1)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
                
                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                # Повторное включение второго канала, новый первый канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
            
                    print(f"Выбранный новый первый канал: {channel_number}, второй канал совпадает с действующим")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем первый канал с новыми параметрами, второй канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (1,0)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)    

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num:
                # Включение нового частотного канала,
                # оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Новый выбранный канал: {channel_number}")
                    print("Первый и третий модемы слышат друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    new_commutation = (0,2,2,0)
                    restart_channels = (1,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.modem_1_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение того же канала,
                # Третий модем слышит первого, первый не слышит третий
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Третий модем слышит первого, первый не слышит третий")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_2_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch2_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (0,2,2,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch2_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_1_RX_ch_num:
                # Повторное включение того же канала,
                # первый модем слышит третьего, третий не слышит первого
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Первый модем слышит третьего, третий не слышит первого")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch1_noise_already_on:
                    #     self.ampl_mult = [0, 1]
                    #     self.en_noise = [1, 0]
                    #     restart_channels = (1,0)
                    #     new_commutation = (0,2,2,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch1_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_3_RX_ch_num:
                # Включение нового частотного канала,
                # третий модем слышит первого, первый не слышит третьего.
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    restart_channels = (1,0)
                    print(f"Выбранный канал: {channel_number}")
                    print("Третий модем слышит первого, первый не слышит третьего")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch2_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch2_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_1_RX_ch_num:
                # первый модем слышит третьего, третий не слышит первого
                    self.current_working_pair1 = [1,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    self.ampl_mult = [0, 1]
                    # self.en_noise = [1, 0]
                    restart_channels = (0,1)
                    print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                    print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                    print(f"Выбранный канал: {channel_number}")
                    print("Первый модем слышит третьего, третий не слышит первого")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch1_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch1_noise_already_on = True
                    # else:
                    #     restart_channels = (0,1)
                    new_commutation = (0,2,2,0)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение того же канала,
                # Второй и третий модемы оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_2_TX_ch_num
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Второй и третий модемы оба слышат друг друга - симметричный канал.")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение первого канала, новый второй канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num

                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Выбранный новый второй канал: {channel_number}, первый канал совпадает с действующим")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем второй канал с новыми параметрами, первый канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (0,1)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num and\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение второго канала, новый первый канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    
                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный новый первый канал: {channel_number}, второй канал совпадает с действующим")
                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Запускаем первый канал с новыми параметрами, второй канал продолжает выполнение с действующими")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    restart_channels = (1,0)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num:
                # Включение нового частотного канала,
                # оба слышат друг друга - симметричный канал.
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num
                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    
                    print(f"Новый выбранный канал: {channel_number}")
                    print("Второй и третий модемы друг друга - симметричный канал")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    self.ampl_mult = [1, 1]
                    # self.en_noise = [0, 0]
                    new_commutation = (1,2,2,1)
                    restart_channels = (1,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_3_RX_ch_num:
                # Повторное включение того же канала,
                # Третий модем слышит второго, второй не слышит третий
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Третий модем слышит второго, второй не слышит третий")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_2_TX_ch_num}, rx3 - {self.new_modem_2_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch2_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (1,2,2,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch2_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                     self.modem_3_TX_ch_num == self.modem_2_RX_ch_num:
                # Повторное включение того же канала,
                # Второй модем слышит третьего, третий не слышит второго
                    self.current_working_pair1 = [2,3]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Второй модем слышит третьего, третий не слышит второго")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch1_noise_already_on:
                    #     self.ampl_mult = [0, 1]
                    #     self.en_noise = [1, 0]
                    #     restart_channels = (1,0)
                    #     new_commutation = (1,2,2,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    #     self.ch1_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_3_RX_ch_num:
                # Включение нового частотного канала,
                # Третий модем слышит второго, второй не слышит третий
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    
                    print(f"Выбранный канал: {channel_number}")
                    print("Третий модем слышит второго, второй не слышит третий")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch2_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch2_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    restart_channels = (1,0)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch1_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_3_TX_ch_num == self.new_modem_2_RX_ch_num:
                # Второй модем слышит третьего, третий не слышит второго
                    self.current_working_pair1 = [2,3]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_3_TX_ch_num
                    self.ampl_mult = [0, 1]
                    # self.en_noise = [1, 0]
                    print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                    print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                    print(f"Выбранный канал: {channel_number}")
                    print("Второй модем слышит третьего, третий не слышит второго")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    # if not self.ch1_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch1_noise_already_on = True
                    # else:
                    #     restart_channels = (0,1)
                    restart_channels = (0,1)
                    new_commutation = (1,2,2,1)
                    self.start_sim(self.sim_handler1, channel_number, restart_channels, new_commutation)
                    # self.ch2_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                else:
                    # Третий модем никого не слышит и третьего модема никто не слышит
                    self.modem_3_RX_ch_num = self.new_modem_3_RX_ch_num
                    self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = 1
                    self.ampl_mult = [0, 0]
                    # self.en_noise = [1, 1]
                    print(f"Третий модем никого не слышит и третьего модема никто не слышит: tx3 - {self.new_modem_3_TX_ch_num}, rx3 - {self.new_modem_3_RX_ch_num}")
                    print("Процесс симуляции остановлен!")
                    if 3 in self.current_working_pair1:
                        self.sim_handler1.ch1_stop_sim()
                        self.sim_handler1.ch2_stop_sim()
                        self.current_working_pair1 = [0,0]

                    # if self.ch1_noise_already_on == self.ch2_noise_already_on == False:
                    #     restart_channels = (1,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch1_noise_already_on == False:
                    #     restart_channels = (1,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch2_noise_already_on == False:
                    #     restart_channels = (0,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # self.ch1_noise_already_on = True
                    # self.ch2_noise_already_on = True

                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.current_modem == 4:

                if self.new_modem_1_TX_ch_num == self.new_modem_4_RX_ch_num ==\
                   self.modem_1_TX_ch_num == self.modem_4_RX_ch_num:
                # Повторное включение того же канала,
                # Четвёртый модем слышит первого, первый не слышит четвёртый.
                    self.current_working_pair2 = [1,4]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    # self.modem_3_TX_ch_num = self.new_modem_3_TX_ch_num

                    channel_number = self.modem_1_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Четвёртый модем слышит первого, первый не слышит четвёртый")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch4_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (0,3,3,0)
                    #     self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    #     self.ch4_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_1_TX_ch_num == self.new_modem_4_RX_ch_num:
                # Включение нового частотного канала,
                # Четвёртый модем слышит первого, первый не слышит четвёртый.
                    self.current_working_pair2 = [1,4]
                    self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                    self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    
                    channel_number = self.modem_1_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    restart_channels = (1,0)
                    print(f"Выбранный канал: {channel_number}")
                    print("Четвёртый модем слышит первого, первый не слышит четвёртый")
                    print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    # if not self.ch4_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch4_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    
                    new_commutation = (0,3,3,0)

                    self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    # self.ch3_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_4_RX_ch_num ==\
                     self.modem_2_TX_ch_num == self.modem_4_RX_ch_num:
                # Повторное включение того же канала,
                # Четвёртый слышит второго, второй не слышит четвёртого.
                    self.current_working_pair1 = [2,4]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num

                    channel_number = self.modem_2_TX_ch_num
                    
                    print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                    print("Четвёртый слышит второго, второй не слышит четвёртого.")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    print("Процесс симуляции продолжается со старыми значениями параметров канала")
                    # if not self.ch4_noise_already_on:
                    #     self.ampl_mult = [1, 0]
                    #     self.en_noise = [0, 1]
                    #     restart_channels = (0,1)
                    #     new_commutation = (1,3,3,1)
                    #     outs_on_off = (1,0)
                    #     self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation, outs_on_off)
                    #     self.ch4_noise_already_on = True
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                elif self.new_modem_2_TX_ch_num == self.new_modem_4_RX_ch_num:
                # Включение нового частотного канала,
                # Четвёртый слышит второго, второй не слышит четвёртого.
                    self.current_working_pair1 = [2,4]
                    self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                    self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    
                    channel_number = self.modem_2_TX_ch_num
                    self.ampl_mult = [1, 0]
                    # self.en_noise = [0, 1]
                    
                    print(f"Выбранный канал: {channel_number}")
                    print("Второй слышит первого, первый не слышит второй")
                    print(f"Комбинация номеров каналов: tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}, rx4 - {self.new_modem_4_RX_ch_num}")
                    # if not self.ch4_noise_already_on:
                    #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                    #     self.ch4_noise_already_on = True
                    # else:
                    #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                    restart_channels = (1,0)

                    new_commutation = (1,3,3,1)
            
                    self.start_sim(self.sim_handler2, channel_number, restart_channels, new_commutation)
                    self.ch3_noise_already_on = False
                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

                else:
                    # Четвёртый модем никого не слышит и четвёртого модема никто не слышит
                    self.modem_4_RX_ch_num = self.new_modem_4_RX_ch_num
                    # self.modem_4_TX_ch_num = self.new_modem_4_TX_ch_num

                    channel_number = 1
                    self.ampl_mult = [0, 0]
                    # self.en_noise = [1, 1]
                    print(f"Четвёртый модем никого не слышит и четвёртого модема никто не слышит: rx4 - {self.new_modem_4_RX_ch_num}")
                    print("Процесс симуляции остановлен!")
                    if 4 in self.current_working_pair2:
                        self.sim_handler2.ch1_stop_sim()
                        self.sim_handler2.ch2_stop_sim()
                        self.current_working_pair2 = [0,0]

                    # if self.ch1_noise_already_on == self.ch2_noise_already_on == False:
                    #     restart_channels = (1,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch1_noise_already_on == False:
                    #     restart_channels = (1,0)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # elif self.ch2_noise_already_on == False:
                    #     restart_channels = (0,1)
                    #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                    # self.ch1_noise_already_on = True
                    # self.ch2_noise_already_on = True

                    self.t1 = datetime.datetime.now()
                    self.data_to_send = self.data_to_read
                    self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

        else:
            if None in [self.new_modem_1_TX_ch_num, self.new_modem_1_RX_ch_num, \
                        self.new_modem_2_TX_ch_num, self.new_modem_2_RX_ch_num]:
                if None in [self.new_modem_1_TX_ch_num, self.new_modem_1_RX_ch_num]:
                    print(f'Не получены номера каналов первого модема, ожидание...\n')
                if None in [self.new_modem_2_TX_ch_num, self.new_modem_2_RX_ch_num]:
                    print(f'Не получены номера каналов второго модема, ожидание...\n')
                return

            if self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num ==\
            self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num ==\
            self.modem_1_TX_ch_num == self.modem_2_RX_ch_num ==\
            self.modem_2_TX_ch_num == self.modem_1_RX_ch_num:
            # Повторное включение того же канала,
            # оба слышат друг друга - симметричный канал.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                channel_number = self.modem_1_TX_ch_num
                print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                print("Оба слышат друг друга - симметричный канал")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Процесс симуляции продолжается со старыми значениями параметров канала")
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num and\
                self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                self.modem_1_TX_ch_num == self.modem_2_RX_ch_num:
            # Повторное включение первого канала, новый второй канал.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                channel_number = self.modem_2_TX_ch_num
                print("Оба слышат друг друга - симметричный канал")
                print(f"Выбранный новый второй канал: {channel_number}, первый канал совпадает с действующим")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Запускаем второй канал с новыми параметрами, первый канал продолжает выполнение с действующими")
                self.ampl_mult = [1, 1]
                # self.en_noise = [0, 0]
                restart_channels = (0,1)
                self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch2_noise_already_on = False
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num and\
                self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                self.modem_2_TX_ch_num == self.modem_1_RX_ch_num:
            # Повторное включение второго канала, новый первый канал.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                
                channel_number = self.modem_1_TX_ch_num
                print(f"Выбранный новый первый канал: {channel_number}, второй канал совпадает с действующим")
                print("Оба слышат друг друга - симметричный канал")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Запускаем первый канал с новыми параметрами, второй канал продолжает выполнение с действующими")
                self.ampl_mult = [1, 1]
                # self.en_noise = [0, 0]
                restart_channels = (1,0)
                self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch1_noise_already_on = False
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num ==\
            self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num:
            # Включение нового частотного канала,
            # оба слышат друг друга - симметричный канал.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                channel_number = self.modem_1_TX_ch_num
                self.ampl_mult = [1, 1]
                # self.en_noise = [0, 0]
                print(f"Новый выбранный канал: {channel_number}")
                print("Оба слышат друг друга - симметричный канал")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                self.ampl_mult = [1, 1]
                # self.en_noise = [0, 0]
                restart_channels = (1,1)
                self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch1_noise_already_on = False
                # self.ch2_noise_already_on = False
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            
            elif self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num ==\
                self.modem_1_TX_ch_num == self.modem_2_RX_ch_num:
            # Повторное включение того же канала,
            # второй слышит первого, первый не слышит второй.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                channel_number = self.modem_1_TX_ch_num
                print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                print("Второй слышит первого, первый не слышит второй")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Процесс симуляции продолжается со старыми значениями параметров канала")
                # if not self.ch2_noise_already_on:
                #     self.ampl_mult = [1, 0]
                #     self.en_noise = [0, 1]
                #     restart_channels = (0,1)
                #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                #     self.ch2_noise_already_on = True
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            
            elif self.new_modem_1_TX_ch_num == self.new_modem_2_RX_ch_num:
            # Включение нового частотного канала,
            # втрой слышит первого, первый не слышит второй.
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                channel_number = self.modem_1_TX_ch_num
                self.ampl_mult = [1, 0]
                # self.en_noise = [0, 1]
                print(f"Выбранный канал: {channel_number}")
                print("Второй слышит первого, первый не слышит второй")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                # if not self.ch2_noise_already_on:
                #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                #     self.ch2_noise_already_on = True
                # else:
                #     restart_channels = (1,0)  # Рестартим только первый канал, т.к. во втором канале уже генерируется белый шум
                restart_channels = (1,0)
                self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch1_noise_already_on = False
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num ==\
                self.modem_2_TX_ch_num == self.modem_1_RX_ch_num:
            # Повторное включение того же канала,
            # первый слышит второго, второй не слышит первого
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                channel_number = self.modem_2_TX_ch_num
                print(f"Выбранный канал: {channel_number} совпадает с действующим, дополнительных действий не требуется")
                print("Первый слышит второго, второй не слышит первого")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Процесс симуляции продолжается со старыми значениями параметров канала")
                # if not self.ch1_noise_already_on:
                #     self.ampl_mult = [0, 1]
                #     self.en_noise = [1, 0]
                #     restart_channels = (1,0)
                #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                #     self.ch1_noise_already_on = True
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

            elif self.new_modem_2_TX_ch_num == self.new_modem_1_RX_ch_num:
            # первый слышит второй, второй не слышит первого
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num

                channel_number = self.modem_2_TX_ch_num
                self.ampl_mult = [0, 1]
                # self.en_noise = [1, 0]
                print(f"Выбранный канал: {channel_number}")
                print("Первый слышит второго, второй не слышит первого")
                print(f"Комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                # if not self.ch1_noise_already_on:
                #     restart_channels = (1,1)  # Рестартим оба канала, т.к. в канале с несовпадающими номерами каналов должен генерироваться белый шум
                #     self.ch1_noise_already_on = True
                # else:
                #     restart_channels = (0,1)
                restart_channels = (0,1)
                self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch2_noise_already_on = False
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            
            else:
                # никто никого не слышит
                self.modem_1_RX_ch_num = self.new_modem_1_RX_ch_num
                self.modem_1_TX_ch_num = self.new_modem_1_TX_ch_num
                self.modem_2_RX_ch_num = self.new_modem_2_RX_ch_num
                self.modem_2_TX_ch_num = self.new_modem_2_TX_ch_num
                channel_number = 1
                self.ampl_mult = [0, 0]
                # self.en_noise = [1, 1]
                print(f"Недопустимая комбинация номеров каналов: tx1 - {self.new_modem_1_TX_ch_num}, rx1 - {self.new_modem_1_RX_ch_num}, tx2 - {self.new_modem_2_TX_ch_num}, rx2 - {self.new_modem_2_RX_ch_num}")
                print("Процесс симуляции остановлен!")
                # if self.ch1_noise_already_on == self.ch2_noise_already_on == False:
                #     restart_channels = (1,1)
                #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # elif self.ch1_noise_already_on == False:
                #     restart_channels = (1,0)
                #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # elif self.ch2_noise_already_on == False:
                #     restart_channels = (0,1)
                #     self.start_sim(self.sim_handler1, channel_number, restart_channels)
                # self.ch1_noise_already_on = True
                # self.ch2_noise_already_on = True

                if self.sim_handler1.ch1_flow_graph_is_running:
                    self.sim_handler1.ch1_stop_sim()  # Останавливаем симуляцию для переконфигурирования симулятора
                    self.sim_handler1.ch2_stop_sim()

                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)

    def run(self):
        try:
            while True:
                if not self.server_is_running:
                    serversocket = socket.socket()
                    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        serversocket.bind((self.host, self.port))
                        print(f"Сервер создан с параметрами: адрес {self.host}, порт {self.port}\nОжидание подключения клиентов...\n")
                    except socket.error:
                        print("Недопустимый адрес сервера или номер порта\n")
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(("8.8.8.8", 80))
                        stock_ip = s.getsockname()[0]
                        print(f"Сервер будет запущен с параметрами:  адрес - {stock_ip}, порт - 8080\nОжидание подключения клиентов...\n")
                        serversocket.bind((stock_ip, 8080))
                        
                    serversocket.listen()
                    serversocket.setblocking(False)  # Переводим сервер в неблокирующий режим, чтобы избежать застреваний в accept
                    
                    self.server_is_running = True
                    
                    self.epoll = select.epoll()  # Создаем объект epoll
                    # Регистрируем наш интерес к событию чтения нашего сервера (его файлового дескриптора)
                    # Оно будет срабатывать каждый раз когда сервер акцептит новое соединение
                    self.epoll.register(serversocket.fileno(), select.EPOLLIN)                                        
                            
                if self.stop_server_flag == True:  # Останавливаем адаптацию по частоте при выставлении флага (по нажатию на кнопку "остановить симуляцию")
                    print("Сервер остановлен\n")
                    self.sim_handler1.ch1_stop_sim()
                    self.sim_handler1.ch2_stop_sim()
                    if self.teamwork:
                        self.sim_handler1.ch1_stop_sim()
                        self.sim_handler1.ch2_stop_sim()
                    self.new_modem_1_RX_ch_num = None  # Новый номер приемного канала модема подключенного к первому входу звуковой карты
                    self.new_modem_1_TX_ch_num = None  # Новый номер передающего канала модема подключенного к первому входу звуковой карты
                    self.new_modem_2_RX_ch_num = None  # Новый номер приемного канала модема подключенного ко второму входу звуковой карты
                    self.new_modem_2_TX_ch_num = None  # Новый номер передающего канала модема подключенного ко второму входу звуковой карты
                    self.new_modem_3_RX_ch_num = None  # Новый номер приемного канала модема подключенного к третьему входу звуковой карты
                    self.new_modem_3_TX_ch_num = None  # Новый номер передающего канала модема подключенного к третьему входу звуковой карты
                    self.new_modem_4_RX_ch_num = None  # Новый номер приемного канала модема подключенного ко четвёртому входу звуковой карты
                    # self.new_modem_4_TX_ch_num = None  # Новый номер передающего канала модема подключенного ко четвёртому входу звуковой карты
                    self.modem_1_RX_ch_num = -1  # Сбрасываем значения номеров каналов после остановки сервера
                    self.modem_1_TX_ch_num = -1
                    self.modem_2_RX_ch_num = -1
                    self.modem_2_TX_ch_num = -1
                    self.modem_3_RX_ch_num = -1  # Сбрасываем значения номеров каналов после остановки сервера
                    self.modem_3_TX_ch_num = -1
                    self.modem_4_RX_ch_num = -1
                    self.modem_4_TX_ch_num = -1
                    self.epoll.unregister(serversocket.fileno())
                    self.epoll.close()
                    serversocket.close()
                    self.server_is_running = False
                    while self.stop_server_flag == True:
                        time.sleep(0.01)  # Задержка, облегчающая работу процессору, не удалять!!!
                # Спрашиваем объект epoll о том, произошли ли какие либо события 
                # Параметр 1 говорит о том, что мы будем ждать одну секунду
                if not self.epoll.closed:
                    events = self.epoll.poll(1)  
                    for fileno, event in events:  # События возвращаются в виде кортежа с файловым дескриптором и кодом события
                        # Если событие чтения возникло в сокете сервера, тогда создаем новое соединение
                        if fileno == serversocket.fileno():
                            conn, addr = serversocket.accept()
                            conn.setblocking(False)
                            print(f"Подключен клиент с адресом: {addr[0]}")
                            self.conn_map[conn.fileno()] = [conn, addr]
                            self.epoll.register(conn.fileno(), select.EPOLLIN)  # Регистрируем наш интерес к событию чтения соединения с клиентом
                        elif event & select.EPOLLIN:
                            self.data_to_read = self.conn_map[fileno][0].recv(1024)
    #                         print('recv ', self.data_to_read)
                            if self.data_to_read:
                                self.read_data_handler(fileno)
                            else:
                                self.epoll.modify(fileno, 0)
                                self.conn_map[fileno][0].shutdown(socket.SHUT_RDWR)
                        elif event & select.EPOLLOUT:
    #                         print('send ', self.data_to_send)
                            self.conn_map[fileno][0].send(self.data_to_send)
                            self.data_to_send = b""
                            self.epoll.modify(fileno, select.EPOLLIN)
                        elif event & select.EPOLLHUP:  # Обрабатываем дисконнект клиента
                            print(f"Клиент с адресом {self.conn_map[fileno][1][0]} закрыл соединение, ожидание переподключения...\n")
                            self.modem_1_RX_ch_num = None
                            self.modem_1_TX_ch_num = None
                            self.modem_2_RX_ch_num = None
                            self.modem_2_TX_ch_num = None
                            self.modem_3_RX_ch_num = None
                            self.modem_3_TX_ch_num = None
                            self.modem_4_RX_ch_num = None
                            self.modem_4_TX_ch_num = None
                            
                            self.epoll.unregister(fileno)  # Разрегистрируем наш интерес в событиях соединения с клиентом
                            self.conn_map[fileno][0].close()  # Закрываем соединение с клиентом
                            del self.conn_map[fileno]  # Удаляем файловый дескриптор из словаря
#                 else:
#                     self.epoll.modify(fileno, 0)
                time.sleep(0.01)  # Задержка, облегчающая работу процессору, не удалять!!!
        except SystemExit:
            if self.server_is_running:
                self.sim_handler1.ch1_stop_sim()
                self.sim_handler1.ch2_stop_sim()
                if self.teamwork:
                    self.sim_handler2.ch1_stop_sim()
                    self.sim_handler2.ch2_stop_sim()
                self.epoll.unregister(serversocket.fileno())
                self.epoll.close()
                serversocket.close()
                self.server_is_running = False
        finally:
            if self.server_is_running:
                self.sim_handler1.ch1_stop_sim()
                self.sim_handler1.ch2_stop_sim()
                if self.teamwork:
                    self.sim_handler2.ch1_stop_sim()
                    self.sim_handler2.ch2_stop_sim()
                self.epoll.unregister(serversocket.fileno())
                self.epoll.close()
                serversocket.close()
                self.server_is_running = False
                