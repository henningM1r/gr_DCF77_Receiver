# -*- coding: iso-8859-1 -*-

import zmq

import sys
sys.path.append('..')
from python.decoder import Class_DecodeDCF77_common as DCF77


class Class_DecodeDCF77_OOK(DCF77.Class_DecodeDCF77_common):

    def __init__(self):
        super().__init__()

    def decode_startbit(self, bit):
        output = ""

        if bit == 1:
            output += "00: ERROR: Start-bit is 1 instead of 0!\n"
        elif bit == 0:
            output += f"00: Start-bit is 0.\n"
        elif bit == 3:
            output += "00: ERROR: Start-bit is ?.\n"

        return output

    def decode_bitstream(self, bitstream):
        output = ""

        count = len(bitstream)

        if count != 59:
            output += "Decoding error\n"
            output += f"#Received bits: {len(bitstream)}\n"
            return output

        output += "\n=== Minute decoded ===\n"
        output += self.decode_startbit(bitstream[0])

        # NOTE: Decrypting MeteoTime bits 01-14 would violate licenses
        output += "01-14: Weather-info is ignored here.\n"

        output += f"15: Calling bit: {bitstream[15]}\n"

        output += self.decode_clock_change(bitstream[16])

        output += self.decode_summertime(bitstream[17:19])

        output += self.decode_leap_second(bitstream[19])

        output += self.decode_time_info_bit(bitstream[20])

        output += self.decode_clock_time(bitstream)

        output += self.decode_date_weekday(bitstream[36:59])

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
                continue

            elif received_msg == "1":
                bitstream.append(1)
                count += 1
                continue

            # derive current time and date from the bitstream
            elif received_msg == "2" and count == 59:
                output = self.decode_bitstream(bitstream)
                print(output)

                bitstream = []
                # this is also the first zero of the next stream
                count = 0
                continue

            # either too few or to many bits have
            # been received during the decoding step
            elif (received_msg == "2" or
                  received_msg == "2" or
                  count > 59):
                print("Error: More than 59 bits at new minute")
                print(f"#Bits: {len(bitstream)}")

                bitstream = []
                count = 0
                continue
