

import socket
import csv
from threading import Thread
import select
import time
import datetime

import tx1_simulation
import tx2_simulation
import tx3_simulation
import tx4_simulation
import parameters_handler

class ServerHandler(Thread):
    def __init__(self):
        super().__init__(daemon = True)
        self.sim_handler1 = parameters_handler.ParametersMulti(tx1_simulation.tx1_simulation())  # Каждый передатчик будет иметь свой флоуграф
        self.sim_handler2 = parameters_handler.ParametersMulti(tx2_simulation.tx2_simulation())
        self.sim_handler3 = parameters_handler.ParametersMulti(tx3_simulation.tx3_simulation())
        self.sim_handler4 = parameters_handler.ParametersMulti(tx4_simulation.tx4_simulation())
        self.sim_handlers = [self.sim_handler1, self.sim_handler2, self.sim_handler3, self.sim_handler4]  # Лист для быстрого доступа к хэндлерам
        self.host = None
        self.port = None
        self.channels_csv_filename = None
        self.teamwork = None
        self.current_modem = None
        
        self.new_TX_ch = None  # Полученный из сообщения новый передающий канал
        self.new_RX_ch = None  # Полученный из сообщения новый приёмный канал

        self.current_channels_TX_RX = [[0,0], [0,0], [0,0], [0,0]]  # Лист для хранения полученных номеров каналов модемов
      
        self.server_is_running = None  
        self.stop_server_flag = None
        
        self.data_to_read = None
        self.data_to_send = None
        
        self.t1 = None  # Время включения канала
        self.t2 = None  # Время выключения канала
        
        self.conn_map = dict()  # Служит для связи создаваемых объектов соединений с файловыми дескрипторами (числами), адресами модемов и каналами на прием и передачу

    def start_sim(self, sim_handler, channel_num):  
        f = open(self.channels_csv_filename, "r")
        i = 0  # Номер строки в csv файле
        for r in csv.reader(f):
            i += 1
            if i == channel_num + 1:
                floats = map(float, r)
                self.ampl1, self.ampl2, self.tau, self.dop_shift, self.dop_fd, self.snr = floats
                print(f"Параметры симуляции:\n a1 - {self.ampl1}, a2 - {self.ampl2}, tau - {self.tau}, dop_shift - {self.dop_shift}, dop_fd - {self.dop_fd}, snr - {self.snr}")
                print("Процесс симуляции запущен...")
        sim_handler.ampl1 = self.ampl1  # Амплитуда первого луча
        sim_handler.ampl2 = self.ampl2  # Амплитуда второго луча
        sim_handler.tau = self.tau * 0.001  # Задержка второго луча относительно первого
        sim_handler.dop_shift = self.dop_shift  # Доплеровский сдвиг частоты
        sim_handler.dop_fd = self.dop_fd  # Доплеровское уширение (рассеивание)
        sim_handler.snr = self.snr  # Отношение сигнал-шум
        sim_handler.start_sim()
        
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
            allowed_modem_addresses = [addr_1_cfg, addr_2_cfg, addr_3_cfg, addr_4_cfg]
        else:
            addr_1_cfg, addr_2_cfg = map(int, f.read().split())
            allowed_modem_addresses = [addr_1_cfg, addr_2_cfg]
        modem_address = self.data_to_read[0]
        if modem_address in allowed_modem_addresses:
            self.current_modem = allowed_modem_addresses.index(modem_address)
            self.new_TX_ch = self.data_to_read[1]
            self.new_RX_ch = self.data_to_read[2]
            print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
            print(f"Сообщение от {modem_address} модема: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
            self.data_to_send = self.data_to_read
            
        else:
            print(f"Получено сообщение от клиента с адресом: {self.conn_map[fileno][1][0]}")
            print(f"Сообщение: адрес - {modem_address}, tx - {self.data_to_read[1]}, rx - {self.data_to_read[2]}")
            print(f"Адрес модема: {modem_address} не допустим, ожидание...\n")
            self.epoll.modify(fileno, select.EPOLLOUT | select.EPOLLONESHOT)
            return 

        if self.current_channels_TX_RX[self.current_modem][0] != self.new_TX_ch:
            print(f"Выбран новый передающий канал: {self.new_TX_ch}")
            self.sim_handlers[self.current_modem].set_rx_en(0, 0)
            self.sim_handlers[self.current_modem].set_rx_en(1, 0)
            self.sim_handlers[self.current_modem].set_rx_en(2, 0)
            self.sim_handlers[self.current_modem].set_rx_en(3, 0)

            self.current_channels_TX_RX[self.current_modem][0] = self.new_TX_ch
            connected_RX_modems = list()
            for idx, modem_i_TX_RX in enumerate(self.current_channels_TX_RX):
                if modem_i_TX_RX[1] == self.new_TX_ch:
                    connected_RX_modems.append(allowed_modem_addresses[idx])
                    self.sim_handlers[self.current_modem].set_rx_en(idx, 1)
                    print(f"Модем {allowed_modem_addresses[idx]} слышит модем {modem_address}")
            if connected_RX_modems:
                self.start_sim(self.sim_handlers[self.current_modem], self.new_TX_ch)
            else:
                print(f"Никто не слышит модем {modem_address}")
        else:
            print(f"Передающий канал {self.new_TX_ch} не изменился, дополнительных действий не требуется")
            
        if self.current_channels_TX_RX[self.current_modem][1] != self.new_RX_ch:
            print(f"Выбран новый приёмный канал: {self.new_RX_ch}")
            for idx, modem_i_TX_RX in enumerate(self.current_channels_TX_RX):
                if modem_i_TX_RX[0] == self.current_channels_TX_RX[self.current_modem][1] and modem_i_TX_RX[0]!=0:
                    self.sim_handlers[idx].set_rx_en(self.current_modem, 0)
            
            self.current_channels_TX_RX[self.current_modem][1] = self.new_RX_ch
            connected_RX_modems = list()
            for idx, modem_i_TX_RX in enumerate(self.current_channels_TX_RX):
                if modem_i_TX_RX[0] == self.current_channels_TX_RX[self.current_modem][1]:
                    connected_RX_modems.append(allowed_modem_addresses[idx])
                    self.sim_handlers[idx].set_rx_en(self.current_modem, 1)
                    if not self.sim_handlers[idx].flow_graph_is_running:
                        self.start_sim(self.sim_handlers[idx], self.new_RX_ch) 
                    print(f"Модем {modem_address} слышит модем {allowed_modem_addresses[idx]}")
            if not connected_RX_modems:
                print(f"Модем {modem_address} никого не слышит")
        else:
            print(f"Приёмный канал {self.new_RX_ch} не изменился, дополнительных действий не требуется")

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
                    self.current_channels_TX_RX = [[0,0], [0,0], [0,0], [0,0]]
                    for sim_handler in self.sim_handlers:
                        sim_handler.stop_sim()                   
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
                            self.epoll.unregister(fileno)  # Разрегистрируем наш интерес в событиях соединения с клиентом
                            self.conn_map[fileno][0].close()  # Закрываем соединение с клиентом
                            del self.conn_map[fileno]  # Удаляем файловый дескриптор из словаря
                time.sleep(0.01)  # Задержка, облегчающая работу процессору, не удалять!!!
        except SystemExit:
            for sim_handler in self.sim_handlers:
                sim_handler.stop_sim()
            self.epoll.unregister(serversocket.fileno())
            self.epoll.close()
            serversocket.close()
        finally:
            for sim_handler in self.sim_handlers:
                sim_handler.stop_sim()
            self.epoll.unregister(serversocket.fileno())
            self.epoll.close()
            serversocket.close()