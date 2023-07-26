# -*- coding: iso-8859-1 -*-


import numpy as np

from abc import ABC, abstractmethod

class Class_DecodeDCF77_common(ABC):

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

    @abstractmethod
    def decode_startbit(self, bit):
        pass

    def decode_fixed_PM_bits(self, bits):
        output = ""

        # instead of weather bits, there are 9 fixed 1-bits and 5 fixed 0-bits
        if (bits[0:9] == np.ones(9)).all():
            output += "01-09: 9 times 1-bits in DCF77 phase modulation.\n"
        else:
            output += "01-09: ERROR: faulty bit(s) detected.\n"

        if (bits[9:14] == np.zeros(5)).all():
            output += "10-14: 5 times 0-bits in DCF77 phase modulation.\n"
        else:
            output += "10-14: ERROR: faulty bit(s) detected.\n"

        return output

    def decode_clock_change(self, bit):
        output = ""

        if bit == 1:
            output += "16: Clock change.\n"
        elif bit == 0:
            output += "16: No clock change.\n"
        elif bit == 3:
            output += "16: ERROR: Clock change contains an error.\n"

        return output

    def decode_summertime(self, bits):
        output = ""

        # TODO check for error value 3 in the following bits
        if bits[0] == 0 and bits[1] == 1:
            output += "17-18: CET - winter time.\n"
        elif bits[0] == 1 and bits[1] == 0:
            output += "17-18: CEST - summer time.\n"
        elif ((bits[0] == 0 and bits[1] == 0) or
              (bits[0] == 1 and bits[1] == 1)):
            output += "17-18: ERROR: Both CET and CEST are equal!\n"
        else:
            output += "17-18: ERROR: CET/CEST contains errors.\n"

        return output

    def decode_leap_second(self, bit):
        output = ""

        # TODO check for error value 3 in the following bits
        if bit == 1:
            output += "19: Leap second.\n"
        elif bit == 0:
            output += "19: No leap second.\n"

        return output

    def decode_time_info_bit(self, bit):
        output = ""

        # TODO check for error value 3 in the following bits
        if bit == 1:
            output += "20: Begin of time information.\n"
        elif bit == 0:
            output += "20: ERROR: Time-info-bit is 0 instead of 1!\n"

        return output

    def decode_minutes(self, bitstream):
        output = ""

        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^
                    bitstream[3] ^ bitstream[4] ^ bitstream[5] ^
                    bitstream[6] ^ bitstream[7] == 0):
                output += "28: Even parity of minutes successful.\n"
            else:
                output += "28: Even parity of minutes failed.\n"
        else:
            pass

        min_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                    bitstream[1], bitstream[0]], 4)

        min_dec10 = self.decode_BCD([bitstream[6], bitstream[5],
                                     bitstream[4]], 3)

        if min_dec0 != "?" and min_dec10 != "?":
            if min_dec0 > 9 and min_dec10 <= 5:
                output += "ERROR: 1*digit of minute is > 9!\n"
                min_dec0 = "?"
            elif min_dec10 > 5 and min_dec0 <= 9:
                output += "ERROR: 10*digit of minute is > 5!\n"
                min_dec10 = "?"
            elif min_dec10 > 5 and min_dec0 > 9:
                output += "ERROR: 10*digit of minute is > 5!\n"
                output += "ERROR: 1*digit of minute is > 9!\n"
                min_dec0 = "?"
                min_dec10 = "?"
        else:
            output += "ERROR: Minute is ?.\n"
            min_dec0 = "?"
            min_dec10 = "?"

        return [output, min_dec0, min_dec10]

    def decode_hours(self, bitstream):
        output = ""

        # check parity for the hour values
        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^ bitstream[3] ^
                    bitstream[4] ^ bitstream[5] ^ bitstream[6] == 0):
                output += "35: Even parity of hours successful.\n"
            else:
                output += "35: Even parity of hours failed.\n"

        hour_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                     bitstream[1], bitstream[0]], 4)

        hour_dec10 = self.decode_BCD([bitstream[5], bitstream[4]], 2)

        # check hour values
        if hour_dec0 != "?" and hour_dec10 != "?":
            if hour_dec10 == 2 and hour_dec0 > 3:
                output += "ERROR: Hours are greater than 23!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"
            elif hour_dec0 > 9 and hour_dec10 <= 2:
                output += "ERROR: 1*digit of hour is > 9!\n"
                hour_dec0 = "?"
            elif hour_dec10 > 2 and hour_dec0 <= 9:
                output += "ERROR: 10*digit of hour is > 2!\n"
                hour_dec10 = "?"
            elif hour_dec10 > 2 and hour_dec0 > 9:
                output += "ERROR: 1*digit of hour is > 9!\n"
                output += "ERROR: 10*digit of hour is > 2!\n"
                hour_dec0 = "?"
                hour_dec10 = "?"
        else:
            output += "ERROR: Hour is ?.\n"
            hour_dec0 = "?"
            hour_dec10 = "?"

        return [output, hour_dec0, hour_dec10]

    def decode_clock_time(self, bitstream):
        output = ""

        [output_m, min_dec0, min_dec10] = self.decode_minutes(bitstream[21:29])
        [output_h, hour_dec0, hour_dec10] = self.decode_hours(bitstream[29:36])

        output += output_m + output_h

        output += f"21-27 & 29-34: Time: {hour_dec10}{hour_dec0}:" + \
                  f"{min_dec10}{min_dec0}h\n"

        return output

    def decode_weekday(self, bitstream):
        output = ""

        if 3 not in bitstream:
            weekday = self.decode_BCD([bitstream[2], bitstream[1],
                                       bitstream[0]], 3)
        else:
            output += "42-44: ERROR: Weekday is ?.\n"
            return output

        if weekday == 0:
            output += "42-44: ERROR: Weekday is 0.\n"
        elif 1 <= weekday <= 7:
            output += f"42-44: Weekday: {self.weekdays[weekday - 1]}\n"

        return output

    def decode_day(self, bitstream):
        output = ""

        day_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                    bitstream[1], bitstream[0]], 4)
        day_dec10 = self.decode_BCD([bitstream[5], bitstream[4]], 2)

        # check date values day
        if day_dec0 != "?" and day_dec10 != "?":
            if day_dec0 == 0 and day_dec10 == 0:
                output += "ERROR: Day is 00!\n"
                day_dec0 = "?"
                day_dec10 = "?"
            elif day_dec0 > 9 and day_dec10 < 3:
                output += "ERROR: 1*digit of day is > 9!\n"
                day_dec0 = "?"
            elif day_dec10 == 3 and day_dec0 >= 2:
                output += "ERROR: Day is > 31!\n"
                day_dec0 = "?"
                day_dec10 = "?"
        else:
            output += "ERROR: Day is ?.\n"
            day_dec0 = "?"
            day_dec10 = "?"

        return [output, day_dec0, day_dec10]

    def decode_month(self, bitstream):
        output = ""

        month_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                      bitstream[1], bitstream[0]], 4)
        month_dec10 = bitstream[4]

        if month_dec10 == 3:
            month_dec10 = "?"

        # check date values month
        if month_dec0 != "?" and month_dec10 != "?":
            if month_dec0 == 0 and month_dec10 == 0:
                output += "ERROR: Month is 00!\n"
                month_dec0 = "?"
                month_dec10 = "?"
            elif month_dec0 > 9 and month_dec10 < 1:
                output += "ERROR: 1*digit of month is > 9!\n"
                month_dec0 = "?"
            elif month_dec10 == 1 and month_dec0 >= 3:
                output += "ERROR: Month is > 12!\n"
                month_dec0 = "?"
                month_dec10 = "?"
        else:
            output += "ERROR: Month is ?.\n"
            month_dec0 = "?"
            month_dec10 = "?"

        return [output, month_dec0, month_dec10]

    def decode_year(self, bitstream):
        output = ""

        year_dec0 = self.decode_BCD([bitstream[3], bitstream[2],
                                     bitstream[1], bitstream[0]], 4)
        year_dec10 = self.decode_BCD([bitstream[7], bitstream[6],
                                      bitstream[5], bitstream[4]], 4)

        # check date values year
        if year_dec0 != "?" and year_dec10 != "?":
            if year_dec0 > 9 and year_dec10 <= 9:
                output += "ERROR: 1*digit of year is > 9!\n"
                year_dec0 = "?"
            if year_dec10 > 9 and year_dec0 <= 1:
                output += "ERROR: 10*digit of year is > 9!\n"
                year_dec10 = "?"
            elif year_dec10 > 9 and year_dec0 > 9:
                output += "ERROR: Year is > 99!\n"
                year_dec0 = "?"
                year_dec10 = "?"
        else:
            output += "ERROR: Year is ?.\n"
            year_dec0 = "?"
            year_dec10 = "?"

        return [output, year_dec0, year_dec10]

    def decode_date_weekday(self, bitstream):
        output = ""

        [output_d, day_dec0, day_dec10] = \
            self.decode_day(bitstream[0:6])
        [output_m, month_dec0, month_dec10] = \
            self.decode_month(bitstream[9:14])
        [output_y, year_dec0, year_dec10] = \
            self.decode_year(bitstream[14:22])

        output += output_d + output_m + output_y

        output += f"36-41 & 45-57: Date: {day_dec10}{day_dec0}." + \
                  f"{month_dec10}{month_dec0}.{year_dec10}{year_dec0}\n"

        output_w = self.decode_weekday(bitstream[6:9])
        output += output_w

        # check even parity for the date and weekday values
        if 3 not in bitstream:
            if (bitstream[0] ^ bitstream[1] ^ bitstream[2] ^
                    bitstream[3] ^ bitstream[4] ^ bitstream[5] ^
                    bitstream[6] ^ bitstream[7] ^ bitstream[8] ^
                    bitstream[9] ^ bitstream[10] ^ bitstream[11] ^
                    bitstream[12] ^ bitstream[13] ^ bitstream[14] ^
                    bitstream[15] ^ bitstream[16] ^ bitstream[17] ^
                    bitstream[18] ^ bitstream[19] ^ bitstream[20] ^
                    bitstream[21] ^ bitstream[22] == 0):
                output += "58: Even parity of date and weekdays successful.\n"
            else:
                output += "58: ERROR: Even parity of date and weekdays failed.\n"
        else:
            output += "58: ERROR: Even parity of date and weekdays is ?.\n"

        return output

    def decode_minute_mark(self, bit):
        output = ""

        if bit == 0:
            output += "59: Minute mark of DCF77 phase modulation is 0.\n"

        else:
            output += "59: ERROR: Minute mark of DCF77 phase modulation failed, it is not 0.\n"

        return output
