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
    def __init__(self, sim_handler, host = "192.168.1.2", port = 8080, channels_csv_filename = "params.csv"):
        super().__init__(daemon = True)
        self.sim_handler = sim_handler
        self.host = host
        self.port = port
        self.channels_csv_filename = channels_csv_filename
        
        self.modem_1_RX_ch_num = None  # Номер приемного канала модема подключенного к первому входу звуковой карты
        self.modem_1_TX_ch_num = None  # Номер передающего канала модема подключенного к первому входу звуковой карты
        self.modem_2_RX_ch_num = None  # Номер приемного канала модема подключенного ко второму входу звуковой карты
        self.modem_2_TX_ch_num = None  # Номер передающего канала модема подключенного ко второму входу звуковой карты
        
        self.server_is_running = None  
        self.stop_server_flag = None
        
        self.data_to_read = None
        self.data_to_send = None
        
        self.t1 = None  # Время включения канала
        self.t2 = None  # Время выключения канала
        
        self.conn_map = dict()  # Служит для связи создаваемых объектов соединений с файловыми дескрипторами (числами), адресами модемов и каналами на прием и передачу
        
    def start_sim(self, channel_num):  
        f = open(self.channels_csv_filename, "r")
        i = 0  # Номер строки в csv файле
        for r in csv.reader(f):
            i += 1
            if i == channel_num + 1:
                floats = map(float, r)
                self.ampl1, self.ampl2, self.tau, self.dop_shift, self.dop_fd, self.snr = floats
        if any(self.ampl_mult):
            print(f"Параметры симуляции:\n a1 - {self.ampl1}, a2 - {self.ampl2}, tau - {self.tau}, dop_shift - {self.dop_shift}, dop_fd - {self.dop_fd}, snr - {self.snr}")
            print("Процесс симуляции запущен...\n")
        if self.sim_handler.flow_graph_is_running == True:
            self.sim_handler.stop_sim()  # Останавливаем симуляцию для переконфигурирования симулятора
        self.sim_handler.ampl1 = self.ampl1  # Амплитуда первого луча
        self.sim_handler.ampl2 = self.ampl2  # Амплитуда второго луча
        self.sim_handler.tau = self.tau * 0.001  # Задержка второго луча относительно первого
        self.sim_handler.dop_shift = self.dop_shift  # Доплеровский сдвиг частоты
        self.sim_handler.dop_fd = self.dop_fd  # Доплеровское уширение (рассеивание)
        self.sim_handler.snr = self.snr  # Отношение сигнал-шум
        self.sim_handler.on_off_out1 = self.ampl_mult[0]
        self.sim_handler.on_off_out2 = self.ampl_mult[1]
        self.sim_handler.en_silence_noise = self.en_noise
        self.sim_handler.start_sim()  # Запуск симуляции канала
        
    def read_data_handler(self, fileno):
        if self.t1:
            self.t2 = datetime.datetime.now()
            dt = self.t2 - self.t1
            self.t1 = 0
            self.t2 = 0
            print(f"Время до перестройки {dt.seconds}.{dt.microseconds} c.\n")
        f = open('address.cfg', 'r')
        addr_1_cfg, addr_2_cfg = map(int, f.read().split())
        
        modem_address = self.data_to_read[0]
        if modem_address == addr_1_cfg:
            self.modem_1_RX_ch_num = self.data_to_read[2]
            self.modem_1_TX_ch_num = self.data_to_read[1]
        elif modem_address == addr_2_cfg:
            self.modem_2_RX_ch_num = self.data_to_read[2]
            self.modem_2_TX_ch_num = self.data_to_read[1]
        else:
            print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
            print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
            print(f"Адрес модема: {modem_address} не допустим, ожидание...\n")
            return 

        if None in [self.modem_1_TX_ch_num, self.modem_1_RX_ch_num]:
            print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
            print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
            print(f'Не получены номера каналов первого модема, ожидание...\ntx2 - {self.modem_2_TX_ch_num}, rx2 - {self.modem_2_RX_ch_num}\n')
            # self.send(bytearray([0]))
            self.data_to_send = self.data_to_read
            self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            return
#             conn.send(self.data_to_read)
        elif None in [self.modem_2_TX_ch_num, self.modem_2_RX_ch_num]:
            print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
            print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
            print(f'Не получены номера каналов второго модема, ожидание...\ntx1 - {self.modem_1_TX_ch_num}, rx1 - {self.modem_1_RX_ch_num}\n')
            # self.send(bytearray([0]))
            self.data_to_send = self.data_to_read
            self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            return
        else:
            if self.modem_1_TX_ch_num == self.modem_2_RX_ch_num ==\
             self.modem_2_TX_ch_num == self.modem_1_RX_ch_num:
            # оба слышат друг друга симметричный канал
                channel_number = self.modem_1_TX_ch_num
                self.ampl_mult = [1, 1]
                self.en_noise = [0, 0]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Выбраный канал: {channel_number}")
                print(f"Комбинация номеров каналов: tx1 - {self.modem_1_TX_ch_num}, rx1 - {self.modem_1_RX_ch_num}, tx2 - {self.modem_2_TX_ch_num}, rx2 - {self.modem_2_RX_ch_num}")
                self.start_sim(channel_number)
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
#                 conn.send(self.data_to_read)
            elif self.modem_1_TX_ch_num == self.modem_2_RX_ch_num:
            # втрой слышит первого, первый не слышит второй
                channel_number = self.modem_1_TX_ch_num
                self.ampl_mult = [1, 0]
                self.en_noise = [0, 1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Выбраный канал: {channel_number}")
                print(f"Комбинация номеров каналов: tx1 - {self.modem_1_TX_ch_num}, rx1 - {self.modem_1_RX_ch_num}, tx2 - {self.modem_2_TX_ch_num}, rx2 - {self.modem_2_RX_ch_num}")
                self.start_sim(channel_number)
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
#                 conn.send(self.data_to_read)
            elif self.modem_2_TX_ch_num == self.modem_1_RX_ch_num:
            # первый слышит второй, второй не слышит первого
                channel_number = self.modem_2_TX_ch_num
                self.ampl_mult = [0, 1]
                self.en_noise = [1, 0]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Выбраный канал: {channel_number}")
                print(f"Комбинация номеров каналов: tx1 - {self.modem_1_TX_ch_num}, rx1 - {self.modem_1_RX_ch_num}, tx2 - {self.modem_2_TX_ch_num}, rx2 - {self.modem_2_RX_ch_num}")
                self.start_sim(channel_number)
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
#                 conn.send(self.data_to_read)
            else:
                # никто никого не слышит
                channel_number = 1
                self.ampl_mult = [0, 0]
                self.en_noise = [1, 1]
                print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
                print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
                print(f"Недопустимая комбинация номеров каналов: tx1 - {self.modem_1_TX_ch_num}, rx1 - {self.modem_1_RX_ch_num}, tx2 - {self.modem_2_TX_ch_num}, rx2 - {self.modem_2_RX_ch_num}")
                print("Процесс симуляции остановлен!\n")
                self.start_sim(channel_number)
                self.t1 = datetime.datetime.now()
                self.data_to_send = self.data_to_read
                self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
#                 conn.send(self.data_to_read)
#                 if self.sim_handler.flow_graph_is_running == True:
#                     self.sim_handler.stop_sim()  # Останавливаем симуляцию для переконфигурирования симулятора
        
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
                    self.sim_handler.stop_sim()
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
                            
                            self.epoll.unregister(fileno)  # Разрегистрируем наш интерес в событиях соединения с клиентом
                            self.conn_map[fileno][0].close()  # Закрываем соединение с клиентом
                            del self.conn_map[fileno]  # Удаляем файловый дескриптор из словаря
#                 else:
#                     self.epoll.modify(fileno, 0)
                time.sleep(0.01)  # Задержка, облегчающая работу процессору, не удалять!!!
        except SystemExit:
            if self.server_is_running:
                self.sim_handler.stop_sim()
                self.epoll.unregister(serversocket.fileno())
                self.epoll.close()
                serversocket.close()
                self.server_is_running = False
        finally:
            if self.server_is_running:
                self.sim_handler.stop_sim()
                self.epoll.unregister(serversocket.fileno())
                self.epoll.close()
                serversocket.close()
                self.server_is_running = False

