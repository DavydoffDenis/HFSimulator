
import numpy as np
from gnuradio import gr
from math import log, sqrt, exp, pi
import scipy
from scipy.signal import lfilter, lfilter_zi

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block

    def __init__(self, fd=0.1):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Prefilled Selfmade filter',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        
        fs = 100.0
        N = int( sqrt( -log( 0.01,exp(1.0) ) ) / (pi*fd/fs) )
        n = range(-N, N+1)
        z = np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N) + np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N)*1j
        #scipy.fromfile(open("complex_noise_4095_samples"), dtype=scipy.complex64)

        h = list(map (lambda n : exp(-(pi*fd*n/fs)**2), n))
        
        k = sqrt(sum(map(lambda x: x*x, h)))
        self.doppler_ir = list(map(lambda x: x / k, h))
        self.N = N
        _, self.z_init = lfilter(self.doppler_ir, 1.0, z[:2*N], zi = z[:2*N])
        #self.z_init = lfilter_zi(self.doppler_ir, 1.0)
        #self.z_init = z[:2*N]
        #self.z_init = np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N) + np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N)*1j
        self.z_end = list()  # holds the final filter delay values.

    def reinit(self, fd):
        fs = 100.0
        N = int( sqrt( -log( 0.01,exp(1.0) ) ) / (pi*fd/fs) )
        n = range(-N, N+1)
        z = np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N) + np.random.normal(loc=0, scale=np.sqrt(2)/2, size=2*N)*1j
        #scipy.fromfile(open("complex_noise_4095_samples"), dtype=scipy.complex64)

        h = list(map (lambda n : exp(-(pi*fd*n/fs)**2), n))
        
        k = sqrt(sum(map(lambda x: x*x, h)))
        self.doppler_ir = list(map(lambda x: x / k, h))
        self.N = N
        _, self.z_init = lfilter(self.doppler_ir, 1.0, z[:2*N], zi = z[:2*N])
        self.z_end = list()  # Обнуляем начальные условия иначе вылетит ошибка

    def work(self, input_items, output_items):
        #output_items[0][:], self.z_end = lfilter(self.doppler_ir, 1.0, input_items[0], zi = self.z_init)
        if len(self.z_end) == 0:
            output_items[0][:], self.z_end = lfilter(self.doppler_ir, 1.0, input_items[0], zi = self.z_init)
        else:
            output_items[0][:], self.z_end = lfilter(self.doppler_ir, 1.0, input_items[0], zi = self.z_end)
        return len(output_items[0])
        
