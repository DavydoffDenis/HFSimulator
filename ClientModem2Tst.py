from socket import *
from PyQt5.QtCore import QByteArray
import sys
import time

address = 13
reception_channel_number = 8
transmission_channel_number = 1
reception_channel_number1 = 1
transmission_channel_number1 = 1

# print('Address: {} RX: {} TX: {}'.format(address, reception_channel_number, \
#       transmission_channel_number))

# print "trying to how many bytes this number contains:{}".format(bin(address))
modem2 = socket(AF_INET, SOCK_STREAM)
modem2.connect(("localhost", 8080))
try:
    while True:
        if reception_channel_number > 10:
            reception_channel_number = 1
        data = []
        data.append(address)
        data.append(transmission_channel_number)
        data.append(reception_channel_number)
        # print("data:", data)
        modem2.sendall(bytearray(data))
        rec = modem2.recv(3)
        print("received:", rec)
        reception_channel_number += 1
        # transmission_channel_number -= 1
        time.sleep(3)
        # data = []
        # data.append(address)
        # data.append(transmission_channel_number1)
        # data.append(reception_channel_number1)
        # # print("data:", data)
        # modem2.sendall(bytearray(data))
        # rec = modem2.recv(3)
        # print("received:", rec)
        # time.sleep(4)
finally:
    modem2.close()