# DCF77_Receiver
A basic DCF77 receiver, containing 
1) signal demodulation and detection of the DCF77 signal with an SDR using GnuRadio (and Python modules)
2) a simple live decoder of received bits provided by the GnuRadio DCF77 receiver

## gr-DCF77
A basic DCF77 receiver, containing:
+ signal demodulation and detection of the DCF77 signal with an SDR using GNURadio (and Python modules)
+ a simple live decoder of received bits provided by the GNURadio DCF receiver

### Overview
The flowgraph is provided in the examples folder.
+ `DCF77-receiver.grc`
+ each received bit is sent to a ZMQ server at `tcp://127.0.0.1:55555`.
+ `DecodeDCF77.py` decodes the received bits from the ZMQ server upon receiving them. It provides the current time, date, weekday, etc. at each new minute.

### Requirements
The DCF77 receiver was tested with:
+ gnuradio 3.10.1.1 & GNURadio Companion 3.10.1.1
+ Python 3.10.6
+ an SDR receiver capable of receiving in the range of approximately 1kHz - 1MHz
    + e.g. _Airspy Discovery HF+_ is configured and used for this project
+ an antenna, that provides a sufficiently clear DCF77 signal
    + e.g. a simple _YouLoop_ loop antenna was used for this project. Indoor reception should possible, if you are close enough (<1000 km) to the DCF77 transmitter in Mainflingen, Germany. You should put the antenna close to a window.
    +  https://www.ptb.de/cms/en/ptb/fachabteilungen/abt4/fb-44/ag-442/dissemination-of-legal-time/dcf77/reach-of-dcf77.html
+ you might also need some antenna cables and adapters to connect the SDR with the antenna
+ this has been successfully tested in
    + Ubuntu 22.04.2 LTS
    + MS Windows 10
    + MS Windows 11

### Instructions/Setup
+ ensure that the raw DCF77 signal reception at 77,5 kHz is good enough
+ to start the DCF77 receiver, open the flowchart in `/examples/DCF77_receiver.grc`with GNURadio Companion
    + press `run` button
    + set the Gain2 and Gain2 slider values in the DCF77 GUI so that the amplitude of data0 is centered roughly around the value 100
    + adjust the upper_threshold and lower_threshold slider values, if needed
    + after parameter adjustment, the GNURadio Companion debug console should show a debug message each second with either '0' or '1' or 'new message'

+ next, open a terminal or Powershell
    + change to your cloned repository
    + run the DecodeDCF77 with```python3 ./python/decoder/DecodeDCF77.py```
    + the terminal should show the received bits together with a sequence of indices
    + after approximately 2 minutes, DecodeDCF77 should be synchronized with the transmitter. It should provide the current time, date, etc. each minute
    + NOTE: sometimes a bit can not be decoded correctly, e.g. due to bad reception. Then the current frame of the minute is corrupted and both the decoder and detector will produce error messages and will attempt to re-synchronize
    + NOTE: feel free to compare the currently received bits live with: https://www.dcf77logs.de/live. Your signal should only lag a single second.

### REMARKS
+ This project has __not__ been tested with a receiver setup using a sound card.
+ This project has __not__ been tested with other SDR receivers.
+ This project has __not__ been tested with other antennas (e.g. a ferrite antenna).
+ This project has __not__ been tested with a simulated transmission signal yet.
+ A Low Noise Amplifier (LNA) is not needed.
+ The decoder does __not__ evaluate the rare special cases of leap seconds.
+ Even a single lost bit causes the synchronization to fail. Resilience of the Decoder has __not__ been implemented, so that lost bits are simply marked and the current frame of the minute is not completely lost.
+ I'd like to acknowledge that I found some very useful inspiration in https://github.com/duggabe/gr-RTTY-basics, on the bit detector.
