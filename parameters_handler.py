'''
Created on Jul 2, 2020

@author: user
'''
from math import log, sqrt, exp, pi
import time

class Parameters:
    '''
    Отвечает за параметры для потоков симуляции канала
    Запускает и останавливает потоки симуляции канала
    '''

    def __init__(self, ch1_sim_t, ch2_sim_t): 
        self.ch1_sim_t = ch1_sim_t     
        self.ch2_sim_t = ch2_sim_t
        
        self.ampl1 = None  # Амплитуда первого луча
        self.ampl2 = None  # Амплитуда второго луча
        self.tau = None  # Задержка второго луча относительно первого
        self.dop_shift = None  # Доплеровский сдвиг частоты
        self.dop_fd = None  # Доплеровское уширение (рассеивание)
        self.snr = None  # Отношение сигнал-шум
        self.rms = None  # Измеряемое в канале среднеквадратическое отклонение
        self.on_off_out1 = None  # Атрибут отвечает за присутствие или отсутствие выхода 1
        self.on_off_out2 = None  # Атрибут отвечает за присутствие или отсутствие выхода 2
        # self.ch1_en_silence_noise = None  # Включает шум на выходе первого канала когда канал выключен для глушения пролазов
        # self.ch2_en_silence_noise = None  # Включает шум на выходе второго канала когда канал выключен для глушения пролазов
    
        self.ch1_flow_graph_is_running = None  # Показывает, запущен ли поток симуляции первого канала
        self.ch2_flow_graph_is_running = None  # Показывает, запущен ли поток симуляции второго канала
        
        self.samp_rate = 48000
        self.latency = 50e-3
        self.tcp_port = 8080
        
        self.tcpServer = None    
    
    # Возвращает амплитуды лучей из потока симуляции канала
    def get_ampl(self, n=0):
        return self.ch1_sim_t.get_ampl()[0][n]
   
    def get_tau(self):  # Возвращает задержку второго луча относительно первого из потока симуляции канала
        return self.ch1_sim_t.get_tau()
                  
    def get_dop_freq_shift(self):  # Возвращает доплеровский сдвиг из потока симуляции канала
        return self.ch1_sim_t.get_freqShift()
        
    def get_dop_ir(self): 
        return self.ch1_sim_t.get_fd()

    def get_ch1_snr(self):  # Возвращает отношение сигнал/шум превого канала из потока симуляции канала
        return self.ch1_sim_t.get_snr_out_func()
    
    def get_ch2_snr(self):  # Возвращает отношение сигнал/шум второго канала из потока симуляции канала
        return self.ch2_sim_t.get_snr_out_func()
        
    def get_ch1_rms(self):  # Возвращает среднеквадратическое отклонение выходного сигнала из потока симуляции канала
        return self.ch1_sim_t.get_out_rms_func()

    def get_ch2_rms(self):  # Возвращает среднеквадратическое отклонение выходного сигнала из потока симуляции канала
        return self.ch2_sim_t.get_out_rms_func()

    def ch1_start_sim(self):
        self.ch1_sim_t.stop()
        self.ch1_sim_t.wait()
        self.Nbuf = int(self.latency*self.samp_rate)
        self.ch1_sim_t.kN = pow(10.0, (-self.snr / 20.0))
        self.ch1_sim_t.set_ampl([[self.ampl1, self.ampl2], [self.ampl1, self.ampl2]])
        self.ch1_sim_t.set_tau(self.tau)
        self.ch1_sim_t.set_freqShift(self.dop_shift)
        self.ch1_sim_t.set_fd(self.dop_fd)
        self.ch1_sim_t.set_snr(self.snr)
        self.ch1_sim_t.set_vol(self.on_off_out1)
        self.ch1_sim_t.set_en_noise(self.ch1_en_silence_noise)
        self.ch1_sim_t.start(self.Nbuf)
        if self.dop_fd == 0:
            self.ch1_sim_t.set_noSpread(1)
        else:
            self.ch1_sim_t.set_noSpread(0)
        time.sleep(0.01)
        self.ch1_sim_t.stop()
        self.ch1_sim_t.wait()
        self.ch1_sim_t.start(self.Nbuf)
        
        self.ch1_flow_graph_is_running = True  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала запущен

    def ch2_start_sim(self):
        self.ch2_sim_t.stop()
        self.ch2_sim_t.wait()
        self.Nbuf = int(self.latency*self.samp_rate)
        self.ch2_sim_t.kN = pow(10.0, (-self.snr / 20.0))
        self.ch2_sim_t.set_ampl([[self.ampl1, self.ampl2], [self.ampl1, self.ampl2]])
        self.ch2_sim_t.set_tau(self.tau)
        self.ch2_sim_t.set_freqShift(self.dop_shift)
        self.ch2_sim_t.set_fd(self.dop_fd)
        self.ch2_sim_t.set_snr(self.snr)
        self.ch2_sim_t.set_vol(self.on_off_out2)
        self.ch2_sim_t.set_en_noise(self.ch2_en_silence_noise)
        self.Nbuf = int(self.latency*self.samp_rate)
        self.ch2_sim_t.start(self.Nbuf)
        if self.dop_fd == 0:
            self.ch2_sim_t.set_noSpread(1)
        else:
            self.ch2_sim_t.set_noSpread(0)
        time.sleep(0.01)
        self.ch2_sim_t.stop()
        self.ch2_sim_t.wait()
        self.ch2_sim_t.start(self.Nbuf)
        
        self.ch2_flow_graph_is_running = True  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала запущен

    def ch1_stop_sim(self):
        self.ch1_sim_t.stop()
        self.ch1_sim_t.wait()
        #del self.sim_t
        self.ch1_flow_graph_is_running = False  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала остановлен
        
    def ch2_stop_sim(self):
        self.ch2_sim_t.stop()
        self.ch2_sim_t.wait()
        #del self.sim_t
        self.ch2_flow_graph_is_running = False  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала остановлен