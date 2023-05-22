

import tx1_simulation

sim = tx1_simulation.tx1_simulation()
sim.rx2_en=1

sim.run(int(48000*50e-3))