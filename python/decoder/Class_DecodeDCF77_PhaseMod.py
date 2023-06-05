# -*- coding: iso-8859-1 -*-

import numpy as np
import zmq


class Class_DecodeDCF77_PhaseMod():

    def __init__(self):
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

    def decode_BCD(self, bits, length):
        if length != len(bits):
            # lengths missmatch
            return "?"

        list1 = [bits[i] for i in range(0, length)]
        if 3 in list1:
            return "?"

        str1 = ''.join(str(e) for e in list1)
        val = int(str1, 2)

        return val

    def decode_bitstream(self, bitstream):
        output = ""
        count = len(bitstream)

        if count != 60:
            output += "Decoding error\n"
            output += f"#Received bits: {len(bitstream)}\n"
            return output

        # start bit differs from OOK-Version
        if bitstream[0] == 0:
            output += "00_ Start-bit is 0 instead of 1 in DCF77 phase modulation\n"
            return output

        output += "\n=== Minute decoded ===\n"
        output += f"00: Start-bit is {bitstream[0]}\n"

        # instead of weather bits, there are 9 fixed 1-bits. and 5 fixed 0-bits
        if (bitstream[1:10] == np.ones(9)).all():
            output += "01-09: 9 times 1-bits in DCF77 phase modulation\n"
        else:
            output += "01-09: Error, faulty bit(s) detected\n"

        if (bitstream[10:15] == np.zeros(5)).all():
            output += "10-14: 5 times 0-bits in DCF77 phase modulation\n"
        else:
            output += "10-14: Error, faulty bit(s) detected\n"

        output += f"15: Calling bit: {bitstream[15]}\n"

        if bitstream[16] == 1:
            output += "16: Clock change\n"
        elif bitstream[16] == 0:
            output += "16: No clock change\n"

        if bitstream[17] == 0 and bitstream[18] == 1:
            output += "17-18: CET - winter time\n"
        elif bitstream[17] == 1 and bitstream[18] == 0:
            output += "17-18: CEST - summer time\n"

        if bitstream[19] == 1:
            output += "19: Leap second\n"
        elif bitstream[19] == 0:
            output += "19: No leap second\n"

        if bitstream[20] == 1:
            output += "20: Begin of time information\n"
        elif bitstream[20] == 0:
            output += "20: Error, is 1 instead of 0!\n"
            return

        min_dec0 = self.decode_BCD([bitstream[24], bitstream[23],
                                    bitstream[22], bitstream[21]], 4)
        min_dec10 = self.decode_BCD([bitstream[27], bitstream[26],
                                     bitstream[25]], 3)

        # check parity for the minute values
        if (bitstream[21] ^ bitstream[22] ^ bitstream[23] ^
                bitstream[24] ^ bitstream[25] ^ bitstream[26] ^
                bitstream[27] ^ bitstream[28] == 0):
            output += "28: Even parity of minutes successful\n"

        else:
            output += "28: Even parity of minutes failed\n"

        hour_dec0 = self.decode_BCD([bitstream[32], bitstream[31],
                                     bitstream[30], bitstream[29]], 4)
        hour_dec10 = self.decode_BCD([bitstream[34], bitstream[33]], 2)

        # check parity for the hour values
        if (bitstream[29] ^ bitstream[30] ^ bitstream[31] ^ bitstream[32] ^
                bitstream[33] ^ bitstream[34] ^ bitstream[35] == 0):
            output += "35: Even parity of hours successful\n"

        else:
            output += "35: Even parity of hours failed\n"

        output += f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:{min_dec10}{min_dec0}h\n"

        weekday = self.decode_BCD([bitstream[44], bitstream[43], bitstream[42]], 3)

        output += f"42-44: Weekday: {self.weekdays[weekday-1]}\n"

        day_dec0 = self.decode_BCD([bitstream[39], bitstream[38],
                                    bitstream[37], bitstream[36]], 4)
        day_dec10 = self.decode_BCD([bitstream[41], bitstream[40]], 2)

        month_dec0 = self.decode_BCD([bitstream[48], bitstream[47],
                                      bitstream[46], bitstream[45]], 4)
        month_dec10 = bitstream[49]

        year_dec0 = self.decode_BCD([bitstream[53], bitstream[52],
                                     bitstream[51], bitstream[50]], 4)
        year_dec10 = self.decode_BCD([bitstream[57], bitstream[56],
                                      bitstream[55], bitstream[54]], 4)

        output += f"36-41 & 45-57: Date: {day_dec10}{day_dec0}.{month_dec10}" + \
                  f"{month_dec0}.{year_dec10}{year_dec0}\n"

        # check parity for the date and weekday values
        if (bitstream[36] ^ bitstream[37] ^ bitstream[38] ^ bitstream[39] ^
                bitstream[40] ^ bitstream[41] ^ bitstream[42] ^ bitstream[43] ^
                bitstream[44] ^ bitstream[45] ^ bitstream[46] ^ bitstream[47] ^
                bitstream[48] ^ bitstream[49] ^ bitstream[50] ^ bitstream[51] ^
                bitstream[52] ^ bitstream[53] ^ bitstream[54] ^ bitstream[55] ^
                bitstream[56] ^ bitstream[57] ^ bitstream[58] == 0):
            output += "58: Even parity of date and weekdays successful\n"

        else:
            output += "58: Even Parity of date and weekdays failed\n"

        if bitstream[59] == 0:
            output += "59: Minute mark of DCF77 phase modulation is 0\n"

        else:
            output += "59: Minute mark of DCF77 phase modulation failed, it is not 0\n"

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
