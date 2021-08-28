'''
Created on Jul 2, 2020

@author: user
'''
from math import log, sqrt, exp, pi


class Parameters:
    '''
    Отвечает за параметры для потока симуляции канала
    Запускает и останавливает поток симуляции канала
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
        self.en_silence_noise = None  # Включает шум на выходе когда канал выключен для глушения пролазов
        
        self.flow_graph_is_running = None  # Показывает, запущен ли поток симуляции канала
        
        self.samp_rate = 48000
        self.latency = 50e-3
        self.tcp_port = 8080
        
        self.tcpServer = None
        
        #self.sim_t = imitation.imitation()  # Создаем экземпляр класса потока выполнения симуляции канала
        
    
    def get_ampl(self):  # Возвращает амплитуды лучей из потока симуляции канала
        return self.sim_t.get_ampl()
    
    def get_tau(self):  # Возвращает задержку второго луча относительно первого из потока симуляции канала
        return self.sim_t.get_tau()
    
    def get_dop_freq_shift(self):  # Возвращает доплеровский сдвиг из потока симуляции канала
        return self.sim_t.get_freqShift()
        
    def get_dop_ir(self): 
        pass
    
    def get_snr(self):  # Возвращает отношение сигнал/шум из потока симуляции канала
        return self.sim_t.get_snrVecOut()
        
    def get_rms(self):  # Возвращает среднеквадратическое отклонение выходного сигнала из потока симуляции канала
        return self.sim_t.get_outSigRMSVec()

#     def calc_doppler_ir(self, fd):
#         fs = 100.0
# #         print('dop_fd =', fd)
#         if fd <= 0.1:
#             fd = 0.1
#         N = int( sqrt( -log( 0.01,exp(1.0) ) ) / (pi*fd/fs) )
#         #N = 70
# #         print ('N =', N)
#         n = range(-N, N+1)
# #         print('n =', n)
#         h = list(map (lambda n : exp(-(pi*fd*n/fs)**2), n))
#         k = sqrt(sum(map(lambda x: x*x, h)))
#         # print('k =', k)
#         # print('h =', list(map(lambda x: x/k, h)))
#         # print sum(h)
#         # print k
#         return (k,h)

    def restart(self, Nbuf):
        ### Костыли, без них рероутинг ДФД не работает при выполнении
        self.sim_t.stop()
        self.sim_t.wait()
        #time.sleep(2)
        self.sim_t.start(Nbuf)
        ###

    def start_sim(self):
#         print(self.ampl1, self.ampl2, self.tau, self.dop_shift, self.dop_fd, self.snr)
        
        self.sim_t.kN = pow(10.0, (-self.snr / 20.0))
        
        
        self.sim_t.set_ampl([[self.ampl1, self.ampl2], [self.ampl1, self.ampl2]])
        self.sim_t.set_tau(self.tau)
        self.sim_t.set_freqShift(self.dop_shift)
        
#         (k, dopplerIR) = self.calc_doppler_ir(self.dop_fd)
#         self.sim_t.set_doppler_ir(list(map(lambda x: x / k, dopplerIR)) )
        self.sim_t.set_fd(self.dop_fd)
       
        self.sim_t.set_snr(self.snr)
        self.sim_t.set_vol([self.on_off_out1, self.on_off_out2])
        self.sim_t.set_en_noise(self.en_silence_noise)
        
        self.Nbuf = int(self.latency*self.samp_rate)
        self.sim_t.start(self.Nbuf)
        if self.dop_fd == 0:
            self.sim_t.set_noSpread(1)
#             print('Nospread selected')
        else:
            self.sim_t.set_noSpread(0)
#             print('Spread selected')
        self.restart(self.Nbuf)
        
        self.flow_graph_is_running = True  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала запущен

    def fixed_sel_params(self):
        if self.running == 1:  # Проверяем запущен ли поток симуляции канала
            self.fixed_freq_imit_thread.stop()  # Останавливаем поток выполнения
            return 1
        else:
            return 0
            
#     def switch_off_on_out(self):
#         pass
#             
#     def create_adapt(self):
#                    
#         adapt_freq_imit_thread = AsyncServer.ServerThread("localhost", PORT)
#         adapt_freq_imit_thread.start()
#         self.statusBar().showMessage("Адаптация по частоте включена...")
        

    def stop_sim(self):
        self.sim_t.stop()
        self.sim_t.wait()
        #del self.sim_t
        self.flow_graph_is_running = False  # Выставляем флаг, сигнализирующий о том, что поток симуляции канала остановлен

