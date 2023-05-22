

import tx1_simulation
sim_t = tx1_simulation.tx1_simulation()
samp_rate = 48000
latency = 50e-3
Nbuf = int(latency*samp_rate)
sim_t.start(Nbuf)
sim_t.wait()
str1 = None
while True:
    input("Insert RX and en", str1)
    rx, en = map(int, str1.split())
    if rx == 1:
        sim_t.set_rx1_en(en)
    elif rx == 2:
        sim_t.set_rx2_en(en)
    elif rx == 3:
        sim_t.set_rx3_en(en)
    elif rx == 4:
        sim_t.set_rx4_en(en)
