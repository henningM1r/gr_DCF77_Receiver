# -*- coding: iso-8859-1 -*-

import numpy as np
import zmq


weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]

def decode_BCD4(bits):
    list1 = [bits[0], bits[1], bits[2], bits[3]]
    str1 = ''.join(str(e) for e in list1)
    val = int(str1, 2)

    return val

def decode_BCD2(bits):
    list1 = [bits[0], bits[1]]
    str1 = ''.join(str(e) for e in list1)
    val = int(str1, 2)

    return val

def decode_BCD3(bits):
    list1 = [bits[0], bits[1], bits[2]]
    str1 = ''.join(str(e) for e in list1)
    val = int(str1, 2)

    return val

def decode_bitstream(bitstream, count):
    print("\n=== Minute decoded ===")

    if count != 61:
        print("Decoding error")
        print(f"#Received bits: {len(bitstream)}")
        print("\n")
        return

    # start bit differs from OOK-Version
    if bitstream[0] == 0:
        print("00_ Start-bit is 0 instead of 1 in DCF77 phase modulation")
        print("\n")
        return

    print(f"00: Start-bit is {bitstream[0]}")

    # instead of weather bits, there are 9 fixed 1-bits. and 5 fixed 0-bits
    if (bitstream[1:10] == np.ones(9)).all():
        print("01-09: 9 times 1-bits in DCF77 phase modulation")
    else:
        print("01-09: Error, faulty bit(s) detected")

    if (bitstream[10:15] == np.zeros(5)).all():
        print("10-14: 5 times 0-bits in DCF77 phase modulation")
    else:
        print("10-14: Error, faulty bit(s) detected")

    print(f"15: Calling bit: {bitstream[15]}")

    if bitstream[16] == 1:
        print("16: Clock change")
    elif bitstream[16] == 0:
        print("16: No clock change")

    if bitstream[17] == 0 and bitstream[18] == 1:
        print("17-18: CET - winter time")
    elif bitstream[17] == 1 and bitstream[18] == 0:
        print("17-18: CEST - summer time")

    if bitstream[19] == 1:
        print("19: Leap second")
    elif bitstream[19] == 0:
        print("19: No leap second")

    if bitstream[20] == 1:
        print("20: Beginn of time information")
    elif bitstream[20] == 0:
        print("20: Error, is 1 instead of 0!")
        return

    min_dec0 = decode_BCD4([bitstream[24], bitstream[23],
                            bitstream[22], bitstream[21]])
    min_dec10 = decode_BCD3([bitstream[27], bitstream[26],
                             bitstream[25]])

    # check parity for the minute values
    if (bitstream[21] ^ bitstream[22] ^ bitstream[23] ^
            bitstream[24] ^ bitstream[25] ^ bitstream[26] ^
            bitstream[27] ^ bitstream[28] == 0):
        print("28: Even parity of minutes successful")

    else:
        print("28: Even parity of minutes failed")

    hour_dec0 = decode_BCD4([bitstream[32], bitstream[31],
                             bitstream[30], bitstream[29]])
    hour_dec10 = decode_BCD2([bitstream[34], bitstream[33]])

    # check parity for the hour values
    if (bitstream[29] ^ bitstream[30] ^ bitstream[31] ^ bitstream[32] ^
            bitstream[33] ^ bitstream[34] ^ bitstream[35] == 0):
        print("35: Even parity of hours successful")

    else:
        print("35: Even parity of hours failed")

    print(f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:{min_dec10}{min_dec0}")

    weekday = decode_BCD3([bitstream[44], bitstream[43], bitstream[42]])

    print(f"42-44: Weekday: {weekdays[weekday-1]}")

    day_dec0 = decode_BCD4([bitstream[39], bitstream[38],
                            bitstream[37], bitstream[36]])
    day_dec10 = decode_BCD2([bitstream[41], bitstream[40]])

    month_dec0 = decode_BCD4([bitstream[48], bitstream[47],
                              bitstream[46], bitstream[45]])
    month_dec10 = bitstream[49]

    year_dec0 = decode_BCD4([bitstream[53], bitstream[52],
                             bitstream[51], bitstream[50]])
    year_dec10 = decode_BCD4([bitstream[57], bitstream[56],
                              bitstream[55], bitstream[54]])

    print(f"36-41 & 45-57: Date: {day_dec10}{day_dec0}.{month_dec10}"
          f"{month_dec0}.{year_dec10}{year_dec0}")

    # check parity for the date and weekday values
    if (bitstream[36] ^ bitstream[37] ^ bitstream[38] ^ bitstream[39] ^
            bitstream[40] ^ bitstream[41] ^ bitstream[42] ^ bitstream[43] ^
            bitstream[44] ^ bitstream[45] ^ bitstream[46] ^ bitstream[47] ^
            bitstream[48] ^ bitstream[49] ^ bitstream[50] ^ bitstream[51] ^
            bitstream[52] ^ bitstream[53] ^ bitstream[54] ^ bitstream[55] ^
            bitstream[56] ^ bitstream[57] ^ bitstream[58] == 0):
        print("58: Even parity of date and weekdays successful")

    else:
        print("58: Even Parity of date and weekdays failed")

    #print(bitstream)
    #print(len(bitstream))

    if bitstream[59] == 0:
        print("59: Minute mark of DCF77 phase modulation is 0")

    else:
        print("59: Minute mark of DCF77 phase modulation failed, it is not 0")

    print("======================\n")   

def consumer():
    context = zmq.Context()

    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:55555")

    bitstream = []
    count = 1

    while True:
        data = consumer_receiver.recv()
        received_msg = data.decode('ascii')[3:]

        print(f"{count:02d}: {received_msg}")

        if received_msg == "0":
            bitstream.append(0)
            count += 1

        elif received_msg == "1":
            bitstream.append(1)
            count += 1

        # derive current time and date from the bitstream
        if received_msg == "2" and count == 61:
            decode_bitstream(bitstream, count)

            # reset bitstream
            bitstream = []
            count = 1

        # either too few or to many bits have
        # been received during the decoding step
        elif (received_msg == "2" and count < 61):
            print("Error: Insufficient number of bits at new minute")
            print(f"#Bits: {len(bitstream)}")

            # reset bitstream
            bitstream = []
            count = 1

        # too many bits trigger a reset of the current bitstream
        if count > 61:
            print(f"Error: No new minute marker was "
                   "detected at expected time")
            print(f"#Bits: {len(bitstream)}")

            # reset bitstream
            bitstream = []
            count = 1

consumer()
