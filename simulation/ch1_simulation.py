#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: HFS first channel
# Author: Davydov Denis
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from math import sqrt, pi
import ch1_simulation_epy_block_0 as epy_block_0  # embedded python block
import ch1_simulation_epy_block_0_0 as epy_block_0_0  # embedded python block
import time
import threading




class ch1_simulation(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "HFS first channel", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.snr = snr = 1
        self.vol = vol = 1
        self.tau_a = tau_a = 1/100.
        self.tau = tau = 0.002
        self.snr_out_func = snr_out_func = ([0]*3)
        self.samp_rate = samp_rate = 48000
        self.out_sel = out_sel = 0
        self.out_rms_func = out_rms_func = 0
        self.noSpread = noSpread = 1
        self.kN = kN = pow(10.0, (-snr/20.0))
        self.in_sel = in_sel = 2
        self.freqShift = freqShift = 0.0
        self.fd = fd = 1
        self.en_noise = en_noise = 0
        self.doppler_ir = doppler_ir = [0.0016502763167573274, 0.0018854799389366934, 0.002149957633383614, 0.0024466994528029662, 0.002778907461425479, 0.003149998028185868, 0.003563602180973301, 0.00402356375450247, 0.004533935060796761, 0.0050989698117900155, 0.005723113028669535, 0.006410987682800636, 0.007167377828853199, 0.007997208012493867, 0.008905518763040982, 0.00989743801603955, 0.010978148351927763, 0.012152849984840378, 0.013426719489994542, 0.014804864318746317, 0.016292273216847054, 0.01789376273305468, 0.019613920081278834, 0.021457042698902442, 0.023427074925696508, 0.025527542310538734, 0.027761484135525694, 0.030131384827462734, 0.03263910500345486, 0.035285812968654906, 0.03807191754835305, 0.04099700319171279, 0.04405976832879332, 0.04725796799434838, 0.050588361749672524, 0.05404666793605477, 0.057627525278984175, 0.06132446283016882, 0.06512987918400244, 0.0690350318359975, 0.073030037462906, 0.07710388379815894, 0.08124445365265866, 0.08543856149104095, 0.08967200281887802, 0.0939296164688993, 0.09819535969651079, 0.10245239580938088, 0.10668319386560887, 0.1108696397832219, 0.11499315801386097, 0.11903484274903825, 0.12297559745183839, 0.12679628134392928, 0.1304778613306593, 0.13400156771907581, 0.1373490519778611, 0.14050254470705797, 0.14344501193124823, 0.14616030780428022, 0.14863332181791858, 0.15085011864154488, 0.1527980687853246, 0.154465968374505, 0.15584414644656272, 0.15692455833401583, 0.15770086387153975, 0.1581684893637365, 0.15832467246620405, 0.1581684893637365, 0.15770086387153975, 0.15692455833401583, 0.15584414644656272, 0.154465968374505, 0.1527980687853246, 0.15085011864154488, 0.14863332181791858, 0.14616030780428022, 0.14344501193124823, 0.14050254470705797, 0.1373490519778611, 0.13400156771907581, 0.1304778613306593, 0.12679628134392928, 0.12297559745183839, 0.11903484274903825, 0.11499315801386097, 0.1108696397832219, 0.10668319386560887, 0.10245239580938088, 0.09819535969651079, 0.0939296164688993, 0.08967200281887802, 0.08543856149104095, 0.08124445365265866, 0.07710388379815894, 0.073030037462906, 0.0690350318359975, 0.06512987918400244, 0.06132446283016882, 0.057627525278984175, 0.05404666793605477, 0.050588361749672524, 0.04725796799434838, 0.04405976832879332, 0.04099700319171279, 0.03807191754835305, 0.035285812968654906, 0.03263910500345486, 0.030131384827462734, 0.027761484135525694, 0.025527542310538734, 0.023427074925696508, 0.021457042698902442, 0.019613920081278834, 0.01789376273305468, 0.016292273216847054, 0.014804864318746317, 0.013426719489994542, 0.012152849984840378, 0.010978148351927763, 0.00989743801603955, 0.008905518763040982, 0.007997208012493867, 0.007167377828853199, 0.006410987682800636, 0.005723113028669535, 0.0050989698117900155, 0.004533935060796761, 0.00402356375450247, 0.003563602180973301, 0.003149998028185868, 0.002778907461425479, 0.0024466994528029662, 0.002149957633383614, 0.0018854799389366934, 0.0016502763167573274]
        self.ampl = ampl = [[1.0, 0.0], [1.0, 0.0]]

        ##################################################
        # Blocks
        ##################################################
        self.snr_out = blocks.probe_signal_f()
        self.out_rms = blocks.probe_signal_f()
        def _snr_out_func_probe():
          while True:

            val = self.snr_out.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_snr_out_func,val))
              except AttributeError:
                self.set_snr_out_func(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _snr_out_func_thread = threading.Thread(target=_snr_out_func_probe)
        _snr_out_func_thread.daemon = True
        _snr_out_func_thread.start()
        self.single_pole_iir_filter_xx_0_0 = filter.single_pole_iir_filter_ff(2*pi*tau_a/samp_rate, 1)
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(2*pi*tau_a/samp_rate, 1)
        def _out_rms_func_probe():
          while True:

            val = self.out_rms.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_out_rms_func,val))
              except AttributeError:
                self.set_out_rms_func(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _out_rms_func_thread = threading.Thread(target=_out_rms_func_probe)
        _out_rms_func_thread.daemon = True
        _out_rms_func_thread.start()
        self.low_pass_filter_2 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                1550,
                100,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_1_0 = filter.interp_fir_filter_ccf(
            int(samp_rate/100),
            firdes.low_pass(
                ampl[0][1]*(samp_rate/100.0),
                samp_rate,
                50,
                25,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_1 = filter.interp_fir_filter_ccf(
            int(samp_rate/100),
            firdes.low_pass(
                ampl[0][0]*(samp_rate/100.0),
                samp_rate,
                50,
                25,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                1750+100,
                600,
                window.WIN_HAMMING,
                6.76))
        self.epy_block_0_0 = epy_block_0_0.blk(fd=fd)
        self.epy_block_0 = epy_block_0.blk(fd=fd)
        self.blocks_selector_2 = blocks.selector(gr.sizeof_float*1,0,out_sel)
        self.blocks_selector_2.set_enabled(True)
        self.blocks_selector_1 = blocks.selector(gr.sizeof_float*1,in_sel,0)
        self.blocks_selector_1.set_enabled(True)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_gr_complex*1,noSpread,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,noSpread,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_rms_xx_0_0 = blocks.rms_ff(2*pi*tau_a*10/samp_rate)
        self.blocks_rms_xx_0 = blocks.rms_cf(2*pi*tau_a*100/samp_rate)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0_0_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_3 = blocks.multiply_const_ff(en_noise)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(vol)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(2 * sqrt(ampl[0][0]**2 + ampl[0][1]**2)*2)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(0.5)
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_divide_xx_1 = blocks.divide_ff(1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, int(tau*samp_rate))
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_squared_2_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_2 = blocks.complex_to_mag_squared(1)
        self.blocks_add_xx_1 = blocks.add_vff(1)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.audio_source_0_0_0_0 = audio.source(samp_rate, 'in4', True)
        self.audio_source_0_0_0 = audio.source(samp_rate, 'in3', True)
        self.audio_source_0_0 = audio.source(samp_rate, 'in2', True)
        self.audio_source_0 = audio.source(samp_rate, 'in1', True)
        self.audio_sink_0_0_2 = audio.sink(samp_rate, 'out4', False)
        self.audio_sink_0_0_1 = audio.sink(samp_rate, 'out3', False)
        self.audio_sink_0_0_0 = audio.sink(samp_rate, 'out2', False)
        self.audio_sink_0_0 = audio.sink(samp_rate, 'out1', False)
        self.analog_sig_source_x_2 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1850, 1, 0, 0)
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freqShift, 1, 0, 0)
        self.analog_sig_source_x_0_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1850, 1, 0, 0)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -1850, 1, 0, 0)
        self.analog_noise_source_x_1 = analog.noise_source_c(analog.GR_GAUSSIAN, 1e-0*kN, 3)
        self.analog_fastnoise_source_x_2 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, 1, 1, 8192)
        self.analog_fastnoise_source_x_1 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, 1, 0, 8192)
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_f(analog.GR_GAUSSIAN, 0.3, 0, 8192)
        self.analog_const_source_x_2 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_1_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, ampl[0][1])
        self.analog_const_source_x_1 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, ampl[0][0])
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.analog_const_source_x_1, 0), (self.blocks_selector_0, 1))
        self.connect((self.analog_const_source_x_1_0, 0), (self.blocks_selector_0_0, 1))
        self.connect((self.analog_const_source_x_2, 0), (self.blocks_float_to_complex_1, 1))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blocks_multiply_const_vxx_3, 0))
        self.connect((self.analog_fastnoise_source_x_1, 0), (self.epy_block_0, 0))
        self.connect((self.analog_fastnoise_source_x_2, 0), (self.epy_block_0_0, 0))
        self.connect((self.analog_noise_source_x_1, 0), (self.low_pass_filter_2, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.analog_sig_source_x_2, 0), (self.blocks_multiply_xx_0_0_0_0_0, 1))
        self.connect((self.audio_source_0, 0), (self.blocks_selector_1, 0))
        self.connect((self.audio_source_0_0, 0), (self.blocks_selector_1, 1))
        self.connect((self.audio_source_0_0_0, 0), (self.blocks_selector_1, 2))
        self.connect((self.audio_source_0_0_0_0, 0), (self.blocks_selector_1, 3))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_rms_xx_0_0, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_selector_2, 0))
        self.connect((self.blocks_complex_to_mag_squared_2, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_2_0, 0), (self.single_pole_iir_filter_xx_0_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_0_0_0_0, 0))
        self.connect((self.blocks_divide_xx_1, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.blocks_multiply_xx_0_0_0_0_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_multiply_const_vxx_3, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_multiply_xx_0_0_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_rms_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0_0_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0_0_0_0_0, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_multiply_xx_0_0_0_0_0, 0), (self.blocks_complex_to_mag_squared_2_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_complex_to_mag_squared_2, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.snr_out, 0))
        self.connect((self.blocks_rms_xx_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_rms_xx_0_0, 0), (self.out_rms, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_multiply_xx_0_0_0, 1))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_multiply_xx_0_0_0_0, 1))
        self.connect((self.blocks_selector_1, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_selector_2, 0), (self.audio_sink_0_0, 0))
        self.connect((self.blocks_selector_2, 1), (self.audio_sink_0_0_0, 0))
        self.connect((self.blocks_selector_2, 2), (self.audio_sink_0_0_1, 0))
        self.connect((self.blocks_selector_2, 3), (self.audio_sink_0_0_2, 0))
        self.connect((self.epy_block_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.epy_block_0_0, 0), (self.low_pass_filter_1_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_selector_0, 0))
        self.connect((self.low_pass_filter_1_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.low_pass_filter_2, 0), (self.blocks_multiply_xx_0_0_0_0_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_divide_xx_1, 0))
        self.connect((self.single_pole_iir_filter_xx_0_0, 0), (self.blocks_divide_xx_1, 1))


    def get_snr(self):
        return self.snr

    def set_snr(self, snr):
        self.snr = snr
        self.set_kN(pow(10.0, (-self.snr/20.0)))

    def get_vol(self):
        return self.vol

    def set_vol(self, vol):
        self.vol = vol
        self.blocks_multiply_const_vxx_2.set_k(self.vol)

    def get_tau_a(self):
        return self.tau_a

    def set_tau_a(self, tau_a):
        self.tau_a = tau_a
        self.blocks_rms_xx_0.set_alpha(2*pi*self.tau_a*100/self.samp_rate)
        self.blocks_rms_xx_0_0.set_alpha(2*pi*self.tau_a*10/self.samp_rate)
        self.single_pole_iir_filter_xx_0.set_taps(2*pi*self.tau_a/self.samp_rate)
        self.single_pole_iir_filter_xx_0_0.set_taps(2*pi*self.tau_a/self.samp_rate)

    def get_tau(self):
        return self.tau

    def set_tau(self, tau):
        self.tau = tau
        self.blocks_delay_0.set_dly(int(self.tau*self.samp_rate))

    def get_snr_out_func(self):
        return self.snr_out_func

    def set_snr_out_func(self, snr_out_func):
        self.snr_out_func = snr_out_func

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_2.set_sampling_freq(self.samp_rate)
        self.blocks_delay_0.set_dly(int(self.tau*self.samp_rate))
        self.blocks_rms_xx_0.set_alpha(2*pi*self.tau_a*100/self.samp_rate)
        self.blocks_rms_xx_0_0.set_alpha(2*pi*self.tau_a*10/self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 1750+100, 600, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.ampl[0][0]*(self.samp_rate/100.0), self.samp_rate, 50, 25, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(self.ampl[0][1]*(self.samp_rate/100.0), self.samp_rate, 50, 25, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_2.set_taps(firdes.low_pass(1, self.samp_rate, 1550, 100, window.WIN_HAMMING, 6.76))
        self.single_pole_iir_filter_xx_0.set_taps(2*pi*self.tau_a/self.samp_rate)
        self.single_pole_iir_filter_xx_0_0.set_taps(2*pi*self.tau_a/self.samp_rate)

    def get_out_sel(self):
        return self.out_sel

    def set_out_sel(self, out_sel):
        self.out_sel = out_sel
        self.blocks_selector_2.set_output_index(self.out_sel)

    def get_out_rms_func(self):
        return self.out_rms_func

    def set_out_rms_func(self, out_rms_func):
        self.out_rms_func = out_rms_func

    def get_noSpread(self):
        return self.noSpread

    def set_noSpread(self, noSpread):
        self.noSpread = noSpread
        self.blocks_selector_0.set_input_index(self.noSpread)
        self.blocks_selector_0_0.set_input_index(self.noSpread)

    def get_kN(self):
        return self.kN

    def set_kN(self, kN):
        self.kN = kN
        self.analog_noise_source_x_1.set_amplitude(1e-0*self.kN)

    def get_in_sel(self):
        return self.in_sel

    def set_in_sel(self, in_sel):
        self.in_sel = in_sel
        self.blocks_selector_1.set_input_index(self.in_sel)

    def get_freqShift(self):
        return self.freqShift

    def set_freqShift(self, freqShift):
        self.freqShift = freqShift
        self.analog_sig_source_x_1.set_frequency(self.freqShift)

    def get_fd(self):
        return self.fd

    def set_fd(self, fd):
        self.fd = fd

    def get_en_noise(self):
        return self.en_noise

    def set_en_noise(self, en_noise):
        self.en_noise = en_noise
        self.blocks_multiply_const_vxx_3.set_k(self.en_noise)

    def get_doppler_ir(self):
        return self.doppler_ir

    def set_doppler_ir(self, doppler_ir):
        self.doppler_ir = doppler_ir

    def get_ampl(self):
        return self.ampl

    def set_ampl(self, ampl):
        self.ampl = ampl
        self.analog_const_source_x_1.set_offset(self.ampl[0][0])
        self.analog_const_source_x_1_0.set_offset(self.ampl[0][1])
        self.blocks_multiply_const_vxx_1.set_k(2 * sqrt(self.ampl[0][0]**2 + self.ampl[0][1]**2)*2)
        self.low_pass_filter_1.set_taps(firdes.low_pass(self.ampl[0][0]*(self.samp_rate/100.0), self.samp_rate, 50, 25, window.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(self.ampl[0][1]*(self.samp_rate/100.0), self.samp_rate, 50, 25, window.WIN_HAMMING, 6.76))




def main(top_block_cls=ch1_simulation, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start(2400)

    tb.wait()


if __name__ == '__main__':
    main()
