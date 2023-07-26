# -*- coding: iso-8859-1 -*-

import zmq

import sys
sys.path.append('..')
from python.decoder import Class_DecodeDCF77_common as DCF77


class Class_DecodeDCF77_PhaseMod(DCF77.Class_DecodeDCF77_common):

    def __init__(self):
        super().__init__()

    def decode_startbit(self, bit):
        output = ""

        # NOTE the start-bit is inverted when
        # compared to amplitude modulation
        if bit == 1:
            output += "00: Start-bit is 1.\n"
        elif bit == 0:
            output += "00: ERROR: Start-bit is 0 instead of 1!\n"
        elif bit == 3:
            output += "00: ERROR: Start-bit is ?.\n"

        return output

    def decode_bitstream(self, bitstream):
        output = ""

        count = len(bitstream)

        if count != 60:
            output += "Decoding error\n"
            output += f"#Received bits: {len(bitstream)}\n"
            return output

        output += "\n=== Minute decoded ===\n"
        output += self.decode_startbit(bitstream[0])

        output += self.decode_fixed_PM_bits(bitstream[1:15])

        output += f"15: Calling bit: {bitstream[15]}\n"

        output += self.decode_clock_change(bitstream[16])

        output += self.decode_summertime(bitstream[17:19])

        output += self.decode_leap_second(bitstream[19])

        output += self.decode_time_info_bit(bitstream[20])

        output += self.decode_clock_time(bitstream)

        output += self.decode_date_weekday(bitstream[36:59])

        output += self.decode_minute_mark(bitstream[59])

        output += "======================"

        return output

    def consumer(self):
        context = zmq.Context()

        consumer_receiver = context.socket(zmq.PULL)
        consumer_receiver.connect("tcp://127.0.0.1:55555")

        bitstream = []
        count = 0

        while True:
            data = consumer_receiver.recv()
            received_msg = data.decode('ascii')[3:]

            # exit-loop statement: for testing only
            if received_msg == "___EOT":
                consumer_receiver.close()
                context.term()
                break

            print(f"{count:02d}: {received_msg}")

            if received_msg == "0":
                bitstream.append(0)
                count += 1

            elif received_msg == "1":
                bitstream.append(1)
                count += 1

            # derive current time and date from the bitstream
            if received_msg == "2" and count == 60:
                output = self.decode_bitstream(bitstream)
                print(output)

                # reset bitstream
                bitstream = []
                count = 0

            # either too few or to many bits have
            # been received during the decoding step
            elif (received_msg == "2" and count < 60):
                print("Error: Less than 60 bits at new minute")
                print(f"#Bits: {len(bitstream)}")

                # reset bitstream
                bitstream = []
                count = 0

            # too many bits trigger a reset of the current bitstream
            if count > 60:
                print(f"Error: More than 60 bits at new minute")
                print(f"#Bits: {len(bitstream)}")

                # reset bitstream
                bitstream = []
                count = 0
