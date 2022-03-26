from matplotlib import pyplot as plt
import numpy as np
from math import sqrt, pi, exp, log10
import operator
from datetime import date
from telnetlib import Telnet
import time
from builtins import list

mode = input("Добро пожаловать!\nПожалуйста, укажите режим проверки (RMS/DopplerIR/Simple):")
mode = mode.upper()

if mode == "SIMPLE":
    f_center = float(input("Пожалуйста, введите центральную частоту спектра в герцах (1850  Гц):"))
    f_span = float(input("Пожалуйста, введите  ширину спектра в герцах (3100 Гц):"))
    
    with Telnet("192.168.1.101", 5023) as tn:
        data = tn.read_very_eager()
        tn.write(b"*IDN?" + b"\n")
        data = tn.read_until(b"SCPI>")
        print(data.decode("utf8"))
        tn.write(f"CONF:SAN".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f":INPut:COUPling DC".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:FREQ:CENT {f_center}".encode() + b"\n")  
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:FREQ:SPAN {f_span}".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:BWID 1".encode() + b"\n")
        tn.read_until(b"SCPI>")
#         tn.write(f":DISP:WIND:TRAC:Y:RLEV -20 DBM".encode() + b"\n")
#         tn.read_until(b"SCPI>") 
#         tn.write(f"SENS:AVER ON".encode() + b"\n")
#         tn.read_until(b"SCPI>")

elif mode == "RMS":
    
    n = 0
    day = date.today()
    dict = {} #  Словарик для записи значений измеренных снр и последующего измерения среднего снр
    
    with open("Journal", "a") as journal:
        with Telnet("192.168.1.101", 5023) as tn:          
            data = tn.read_very_eager()
            tn.write(b"*IDN?" + b"\n")
            tn.read_until(b"\n")
            data = tn.read_until(b"\n")
            data += tn.read_until(b"\n")
            print(data.decode("utf8"))
            tn.read_until(b"SCPI>")
            
            f_center = float(input("Введите центральную частоту спектра в герцах (1850 Гц):"))
            integ_bw = float(input("Введите ширину интегрируемого спектра в герцах (3100 Гц):"))
            ampl = float(input("Введите амплитуду сигнала без шума (40 мВ):"))
            
            tn.write(f":INPut:COUPling DC".encode() + b"\n")
            tn.read_until(b"SCPI>")
            tn.write(f"CONFigure:CHPower".encode() + b"\n")
            tn.read_until(b"SCPI>")
            tn.write(f":UNIT:POWer W".encode() + b"\n")
            tn.read_until(b"SCPI>")
            tn.write(f"SENS:FREQ:CENT {f_center}".encode() + b"\n")  
            tn.read_until(b"SCPI>")
            tn.write(f":SENSe:CHPower:BANDwidth:INTegration {integ_bw}".encode() + b"\n")
            tn.read_until(b"SCPI>")
            tn.write(f":SENSe:CHPower:FREQuency:SPAN {integ_bw}".encode() + b"\n")
            tn.read_until(b"SCPI>")
            
            
            
            while True:
                #journal.seek(-1)
                #journal.write("\n")
                n += 1
                snr_t = input("Введите снр теоретическое:")
                aver_count = float(input("Введите кол-во усреднений:"))
                print(" ")
                tn.write(f":SENSe:CHPower:AVERage:COUNt {aver_count}".encode() + b"\n")
                tn.read_until(b"SCPI>")
                tn.write(f":SENSe:CHPower:AVERage:STATe ON".encode() + b"\n")
                tn.read_until(b"SCPI>")
                
                input("Подайте на вход симулятора сигнал с шумом, затем нажмите Enter")
                print("Выполняется измерение мощности, ожидайте...")
                tn.write(":READ:CHPower:CHPower?".encode() + b"\n")
                data = tn.read_until(b"SCPI>")
                data = tn.read_until(b"\n")
                Psn = float(data)
                print("Измеренная мощность сигнала с шумом равна: ", Psn, " Вт\n")
                
                input("Подайте на вход симулятора только шум, затем нажмите Enter")
                print("Выполняется измерение мощности, ожидайте...")
                tn.write(":READ:CHPower:CHPower?".encode() + b"\n")
                data = tn.read_until(b"SCPI>")
                data = tn.read_until(b"\n")
                Pn = float(data)
                print("Измеренная мощность шума равна:", Pn, " Вт\n")
                
                Ps = Psn - Pn
                snr = round(10*log10(Ps/Pn), 2)
                
                
                dict.setdefault(snr_t, []).append(snr)
                s = 0
                for x in dict[snr_t]:
                    s += x
                d = round(s/len(dict[snr_t]), 2)
                
                print(f"Отношение сигнал/шум №{n} равняется:{snr}, среднее снр за {len(dict[snr_t])} измерений равняется {d} \n\n")
                journal.write(f"Значение СНР №{n} от {str(day)} при f_center={f_center} Гц, integ_bw={integ_bw} Гц, ampl={ampl} мВ, aver_count={aver_count}, SNR_t={snr_t}, Psn={Psn} Вт и Pn={Pn} Вт равняется:{snr}, среднее снр за {len(dict[snr_t])} измерений равняется {d}\n")
         
elif mode == "DOPPLERIR":
    
    f_center = float(input("Пожалуйста, введите центральную частоту спектра в герцах (1000  Гц):"))
    dop_ir = float(input("Пожалуйста, введите величину доплеровского рассеивания в герцах (10 Гц):"))
    f_span = 3*dop_ir
    
   
    with Telnet("192.168.1.101", 5023) as tn:
        data = tn.read_very_eager()
        tn.write(b"*IDN?" + b"\n")
        data = tn.read_until(b"SCPI>")
        print(data.decode("utf8"))
        tn.write(f"CONF:SAN".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f":INPut:COUPling DC".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:FREQ:CENT {f_center}".encode() + b"\n")  
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:FREQ:SPAN {f_span}".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:BWID 1".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f":DISP:WIND:TRAC:Y:RLEV -20 DBM".encode() + b"\n")
        tn.read_until(b"SCPI>") 
        tn.write(f"SENS:AVER ON".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:AVER:COUN 500".encode() + b"\n")
        tn.read_until(b"SCPI>")
        tn.write(f"SENS:AVER:CLE".encode() + b"\n")
        time.sleep(10)   
        tn.write(b"*OPC?\n")
        tn.read_until(b"SCPI>+1")
        tn.write(b"TRAC:DATA? TRACE1" + b"\n")
        data = tn.read_until(b"SCPI>")
        data = tn.read_until(b"\n")
        print("Выполняется измерение, ожидайте...")
    string = data.decode("utf8")
    
    scpi_list = list()
    for word in string.split(","):
        scpi_list.append(float(word))
#     print(scpi_list)    
        
    FD = 48000 / 8
    fi = 10.
    f0 = 1000
    
    np_array = np.array(scpi_list, dtype = float)
    
    f = np.linspace(985, 1015, 601)
    log_Pxx_den = np_array
    
    spectrumAnal = list(map(lambda f: 1.0/ sqrt(pi*fi*fi/2.0) * exp(-2*(f-f0)**2/fi**2), f))
    log_spectrum_anal = list(map(lambda x: 10*log10(x+1e-6), spectrumAnal))
    
    max_anal = max(log_spectrum_anal)
    max_mesure = max(np_array)
    print('max_anal', max_anal, 'max_mesure', max_mesure)
    log_spectrum_anal = [sp - max_anal for sp in log_spectrum_anal]
    log_Pxx_den = [sp - max_mesure for sp in log_Pxx_den]
    logScale = False
    
    z = list(map(operator.sub, log_Pxx_den, log_spectrum_anal))
    diff = [log_spectrum_anal[i] - log_Pxx_den[i] for i in range(len(log_Pxx_den))]
    from statistics import mean
    meanDiff = mean(diff)
    diff = [x - meanDiff for x in diff]
    print('diff', diff)
    if logScale:
        plt.semilogy(f, log_spectrum_anal, 'r')
    else:
        plt.plot(f, log_spectrum_anal, 'r')
    
    if logScale:
        plt.semilogy(f, log_Pxx_den)
        plt.ylim([1e-7, 1e2])
    else:
        plt.plot(f, log_Pxx_den, 'g')
    
    if logScale:
        plt.semilogy(f, log_Pxx_den)
        plt.ylim([1e-7, 1e2])
    else:
        pass
        plt.plot(f, diff, 'b')
    
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.xlim(-1.5*fi+1e3, 1.5*fi + 1e3)
    plt.show()
