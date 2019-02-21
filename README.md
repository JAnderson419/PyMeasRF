# PNA-SMU-UTILS

A Python module for controlling networked test and measurement equipment, implementing PyVISA.
Currently provides Python drivers for the following test equipment:

* Keithley 2400 SMU - Voltage sourcing, measurements (n # triggered and continuous over time)

* Agilent/Keysight N5245A PNA-X - S-parameter measurements and limited measurement setup

* Agilent/Keysight 33220a Arbitrary Waveform Generator - Basic waveform output and frequency sweeping

* Agilent/Keysight N9030A PXA Signal Analyzer - Measurement triggering with current settings

The module also includes tests that use combinations of these instruments. 
The userTests files contain measurement setups and prototype measurements, while the
pnaSMU and smuMeas files contain general test definitions encased in measurement classes 
with easy to use Python functions. 

pnaSMU is used to make S-parameter measurements co-ordinated with any number of Keithley 2400 SMUs.

smuMeas is used to combine any number of Keithley 2400 SMUs together for measurements, allowing some
parameter analyzer-like functionality.