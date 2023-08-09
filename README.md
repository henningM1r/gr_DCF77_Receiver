# gr_DCF77_Receiver
![Pipeline](https://github.com/henningM1r/gr_DCF77_Receiver/actions/workflows/docker-ci.yml/badge.svg)

This is a basic DCF77 receiver for GNU Radio, containing:
1. signal demodulation and detection of the DCF77 OOK signal with an SDR using GNU Radio (and Python modules)
2. signal demodulation and detection of the DCF77 phase-modulated signal with an SDR using GNU Radio (and Python modules)
2. a simple live decoder of the received OOK bits provided by the GNU Radio DCF77 receiver
3. a simple live decoder of the received phase-modulated bits provided by the GNU Radio DCF77 receiver
4. and additional tools for testing the receivers (especially, if no SDR hardware is available):
+ a DCF77 bit encoder
+ a simulated DCF77 transmitter
+ a simulated DCF77 channel (AWGN)

__DCF77__ (D: Germany, C: carrier wave, F: Frankfurt, 77: 77.5 kHz) is the __German time signal__ in Mainflingen.

### Overview
The __flowgraphs__ are provided in the `examples` folder:
+ `DCF_transmitter.grc`
    + only for simulation
    + includes the OOK signaling
    + includes phase modulated pseudo-random sequences signaling
+ `DCF_channel.grc`
    + only for simulation
+ `DCF77_receiver_OOK.grc`
    + for both SDR reception and for simulation
    + includes detection of the OOK signal
+ `DCF77_receiver_PhaseMod.grc`
    + for both SDR reception and for simulation
    + includes detection of the phase-modulated pseudo-random sequences

Supplementary tools are provided in the `python` folder:
+ `DecodeDCF77_OOK.py` decodes the received OOK bits from a specified ZMQ server upon receiving them. It shows the current time, date, weekday, etc. at each new minute.
+ `DecodeDCF77_PhaseMod.py` decodes the received phase-modulated bits from a specified ZMQ server upon receiving them. It shows the current time, date, weekday, etc. at each new minute.
+ `EncodeDCF77.py` encodes the the current time and publishes bits to a ZMQ-server. 


### Requirements
The DCF77 receiver was tested with:
+ gnuradio & GNU Radio Companion 3.10.1.1 (Linux)
+ Radioconda 2023.02.24 & gnuradio & GNU Radio Companion 3.10.5.1 (Windows)
+ Python 3.10.6
    + PyQt5 5.15.7
    + pyzmq 23.1.0
    + gnuradio-osmosdr 0.2.0
+ An SDR receiver capable of receiving in the range of at least 1 kHz - 1 MHz, e.g. an _Airspy Discovery HF+_ is configured and used for this project.
+ An antenna that provides a sufficiently clear DCF77 signal, e.g. a simple _YouLoop_ loop antenna was used for this project. Indoor reception should probably be possible if you are close enough (<1000 km) to the DCF77 transmitter in Mainflingen, Germany. You should mount the antenna close to a window or outside.
    +  https://www.ptb.de/cms/en/ptb/fachabteilungen/abt4/fb-44/ag-442/dissemination-of-legal-time/dcf77/reach-of-dcf77.html
+ The user might also need some antenna cables and adapters to connect the SDR with the antenna.
+ This project has been successfully tested in:
    + Ubuntu 22.04.2 LTS (recommended)
    + MS Windows 11


### Instructions/Setup

#### Simulation

##### DCF77 On-Off-Keying (OOK) Simulation
+ Open the following 3 flowcharts (DCF77_Transmitter.grc, DCF77_Channel.grc, DCF77_Receiver_OOK.grc) in GNU Radio Companion.
+ Generate the Python files with the "Generate the flowgraph"-button.
+ Open 4 separate terminals (e.g.: T1, T2, T3, T4).
    + Change to your cloned repository in all 4 terminals.
+ T1: Go to ```/examples/DCF77_Transmitter/```
+ Run transmitter with: `python3 DCF77_Transmitter.py`
    + It should be run in the 1st step.
    + A GUI should appear.
    + The terminal should provide additional information continuously.
+ T2: Go to ```/examples/DCF77_Channel/```
+ Run Channel with: `python3 DCF77_Channel.py`
    + It should be run in the 2nd step.
    + A GUI should appear.
+ T3: Go to ```/examples/DCF77_Receiver/```
+ Run Receiver with: `python3 DCF77_Receiver_OOK.py`
    + It should be run in the 3rd step.
    + A GUI should appear.
+ T4: (compare above) go to ```/examples/DCF77_Receiver/```
+ Run the decoder with: `python3 DecodeDCF77_PhaseMod.py`
    + It should be run in the 4th step.
    + The terminal should provide received bits continuously, and a time & date message each minute.

Details on the parameters of the OOK receiver are described further below.

Optionally, you can:
+ Run the `Encode.py`.
+ Adapt the `DCF77_Transmitter.grc` to take the time vector from a TCP source instead of the fixed Vector Source.
+ Note that if the simulation is too slow on an older computer, the new minute might overwrite the current signal. This might lead to an incomplete minute each time.

##### DCF77 Phase Modulation Simulation
+ Open the following flowcharts (DCF77_Transmitter.grc, DCF77_Channel.grc, DCF77_Receiver_PhaseMod.grc) in GNU Radio Companion.
+ Generate the Python files with the "Generate the flowgraph"-button.
+ Open 4 separate terminals (e.g.: T1, T2, T3, T4).
    + Change to your cloned repository in all 4 terminals.
+ T1: Go to ```/examples/DCF77_Transmitter/```
+ Run transmitter with: `python3 DCF77_Transmitter.py`
    + It should be run in the 1st step.
    + A GUI should appear.
    + The terminal should provide additional information continuously.
+ T2: Go to ```/examples/DCF77_Channel/```
+ Run Channel with: `python3 DCF77_Channel.py`
    + It should be run in the 2nd step.
    + A GUI should appear.
+ T3: Go to ```/examples/DCF77_Receiver/```
+ Run Receiver with: `python3 DCF77_Receiver_PhaseMod.py`
    + It should be run in the 3rd step.
    + A GUI should appear.
+ T4: (compare above) go to ```/python/```
+ Run the decoder with: `python3 DecodeDCF77_PhaseMod.py`
    + It should be run in the 4th step.
    + The terminal should provide received bits continuously, and a time & date message each minute.

Details on the parameters of the Phase Modulation receiver are described further below.

#### Signal Reception with SDR

##### DCF77 On-Off-Keying (OOK) with SDR
+ Set up your SDR with your computer.
+ Ensure that the raw DCF77 signal reception at 77.5 kHz is good enough, e.g. using gqrx, SDR# or another signal analysis tool. It should reach at least at approximately -75dB or better.
+ To start the DCF77 receiver, open the flowchart in `/examples/DCF77_Receiver/DCF77_receiver_OOK.grc` with GNU Radio Companion
    + Deactivate/hide the source (and related blocks) from the simulation provided by TCP.
    + Activate/unhide the osmocom source (and related blocks).
    + Press `run` button.
    + Set the Gain2 and Gain2 slider values in the DCF77 GUI so that the amplitude of data0 is centered roughly around the value 100.
    + Adjust the upper_threshold and lower_threshold slider values, if needed.
    + After parameter adjustment, the GNU Radio Companion debug console should show a debug message each second with either '0', '1' or '2' (for new minute).

+ Next, open a terminal or Powershell.
    + Change to your cloned repository.
    + Run the DecodeDCF77 with ```python3 ./python/decoder/DecodeDCF77_OOK.py```.
    + The terminal should show the received bits together with a sequence of indices.
    + after approximately 2 minutes, DecodeDCF77_OOK should be synchronized with the transmitter. It should provide the current time, date, etc. each minute.
    + NOTE: sometimes a bit can not be decoded correctly, e.g. due to bad reception. Then the current frame of the minute is corrupted and both the decoder and detector will produce error messages and will attempt to re-synchronize.
    + NOTE: feel free to compare the currently received bits live with: https://www.dcf77logs.de/live. Your signal should only lag a single second.

##### DCF77 Phase Modulation with SDR
+ Set up your SDR with your computer.
+ Ensure that the raw DCF77 signal reception at 77.5 kHz is good enough, e.g. using gqrx or another signal analysis tool. It should reach at least at approximately -75dB or better.
+ To start the DCF77 receiver, open the flowchart in `/examples/DCF77_Receiver/DCF77_receiver_PhaseMod.grc` with GNU Radio Companion.
    + Deactivate/hide the source (and related blocks) from the simulation provided by TCP.
    + Activate/unhide the osmocom source (and related blocks).
    + Press `run` button.
    + Set the Gain2 slider values in the DCF77 GUI so that the amplitude of data0 is centered roughly around the value 100.
    + Adjust the upper_threshold and lower_threshold slider values, if needed.
    + The sliders for shift_step and shift_poll_freq can be adjusted to avoid phase drift. This parameter should rather not be changed unless you observe phase drift.
    + The slider for chip size changes the number of samples per chip. This parameter should rather not be changed.
    + After parameter adjustment, the GNU Radio Companion debug console should show a debug message each second with either '0', '1' or '2' (for new minute).

+ Next, open a terminal or Powershell.
    + Change to your cloned repository.
    + Run the DecodeDCF77 with ```python3 ./python/decoder/DecodeDCF77_PhaseMod.py```.
    + The terminal should show the received bits together with a sequence of indices.
    + after approximately 2 minutes, DecodeDCF77_PhaseMod should be synchronized with the transmitter. It should provide the current time, date, etc. each minute.
    + NOTE: sometimes a bit can not be decoded correctly, e.g. due to bad reception. Then the current frame of the minute is corrupted and both the decoder and detector will produce error messages and will attempt to re-synchronize.
    + NOTE: feel free to compare the currently received bits live with: https://www.dcf77logs.de/live. Your signal should only lag a single second.

### REMARKS
+ This project has __not__ been tested with other SDR receivers, yet.
+ This project has __not__ been tested with a receiver setup using a sound card.
+ This project has __not__ been tested with other antennas (e.g. a ferrite antenna).
+ A Low Noise Amplifier (LNA) is not needed.
+ The dedicated bits for leap seconds are detected, but the decoders do __not__ specifically act on it, yet.
+ Even a single lost bit during reception causes the synchronization of a full minute to fail. Additional resilience of the decoder has __not__ been implemented yet.
+ The project provides the decoded DCF77 signal more or less in real-time, but it is probably __not__ accurate in terms of milliseconds.
+ Weather information (MeteoTime) is __not__ decoded since it is encrypted and commercially licensed, cf. https://www.meteotime.com/. The simulated encoder only provides random bits at bit positions 1 to 14.
+ I would like to __acknowledge__ that I found some very useful inspiration in https://github.com/duggabe/gr-RTTY-basics on the bit detector.
