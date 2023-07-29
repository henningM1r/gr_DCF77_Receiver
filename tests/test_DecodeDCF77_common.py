# -*- coding: iso-8859-1 -*-

import sys
sys.path.append('..')
from python.decoder import Class_DecodeDCF77_common as DCF77
import unittest


class Test_Class_DecodeDCF77_common(unittest.TestCase):
    # NOTE statement enables testing the methods of an abstract class
    DCF77.Class_DecodeDCF77_common.__abstractmethods__ = set()

    def setUp(self):
        self.my_decoder = DCF77.Class_DecodeDCF77_common()
        self.maxDiff = None

    def test_decode_BCD(self):
        # positive test
        bits = [0, 0, 0, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 0
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 0, 0, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 1
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 0, 0, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 8
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = 15
        self.assertEqual(objective, result)

        # positive test
        bits = [0, 3, 1, 0]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = "?"
        self.assertEqual(objective, result)

        # positive test
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 3)
        objective = 7
        self.assertEqual(objective, result)

        # negative test - too many bits
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 2)
        objective = "?"
        self.assertEqual(objective, result)

        # negative test - too few bits
        bits = [1, 1, 1]
        result = self.my_decoder.decode_BCD(bits, 4)
        objective = "?"
        self.assertEqual(objective, result)

    def test_decode_clock_change(self):
        # positive test - no clock change
        bit = 0
        result = self.my_decoder.decode_clock_change(bit)
        objective = "16: No clock change.\n"
        self.assertEqual(objective, result)

        # positive test - clock change
        bit = 1
        result = self.my_decoder.decode_clock_change(bit)
        objective = "16: Clock change.\n"
        self.assertEqual(objective, result)

    def test_decode_summertime(self):
        # positive test - winter time
        bits = [0, 1]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: CET - winter time.\n"
        self.assertEqual(objective, result)

        # positive test - summer time
        bits = [1, 0]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: CEST - summer time.\n"
        self.assertEqual(objective, result)

        # positive test - error: two zeros
        bits = [0, 0]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: Both CET and CEST are equal!\n"
        self.assertEqual(objective, result)

        # positive test - error: two ones
        bits = [1, 1]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: Both CET and CEST are equal!\n"
        self.assertEqual(objective, result)

        # positive test - error: two ones
        bits = [1, 3]
        result = self.my_decoder.decode_summertime(bits)
        objective = "17-18: ERROR: CET/CEST contains errors.\n"
        self.assertEqual(objective, result)

    def test_decode_leap_second(self):
        # positive test - no leap second
        bits = 0
        result = self.my_decoder.decode_leap_second(bits)
        objective = "19: No leap second.\n"
        self.assertEqual(objective, result)

        # positive test - no leap second
        bits = 1
        result = self.my_decoder.decode_leap_second(bits)
        objective = "19: Leap second.\n"
        self.assertEqual(objective, result)

    def test_decode_time_info_bit(self):
        # positive test - time info bit valid (1)
        bits = 1
        result = self.my_decoder.decode_time_info_bit(bits)
        objective = "20: Begin of time information.\n"
        self.assertEqual(objective, result)

        # positive test - time info bit invalid (0)
        bits = 0
        result = self.my_decoder.decode_time_info_bit(bits)
        objective = "20: ERROR: Time-info-bit is 0 instead of 1!\n"
        self.assertEqual(objective, result)

    def test_decode_minutes(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes failed.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [1, 0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n"
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 10*digit of minute is > 5!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 1*digit of minute is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "28: Even parity of minutes successful.\n" + \
                    "ERROR: 10*digit of minute is > 5!\n" + \
                    "ERROR: 1*digit of minute is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "ERROR: Minute is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 3]
        [result, min_1, min_10] = self.my_decoder.decode_minutes(bits)
        objective = "ERROR: Minute is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

    def test_decode_hours(self):
        bits = [0, 0, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours failed.\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [1, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n"
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 1*digit of hour is > 9!\n" + \
                    "ERROR: 10*digit of hour is > 2!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 0, 1, 0, 0, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: Hours are greater than 23!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [0, 1, 0, 1, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 1*digit of hour is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = 0
        self.assertEqual(objective, min_10)

        bits = [0, 0, 0, 0, 1, 1, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "35: Even parity of hours successful.\n" + \
                    "ERROR: 10*digit of hour is > 2!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 0, 0, 0, 0, 0, 1]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "ERROR: Hour is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

        bits = [3, 3, 0, 0, 0, 0, 0]
        [result, min_1, min_10] = self.my_decoder.decode_hours(bits)
        objective = "ERROR: Hour is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, min_1)
        objective = "?"
        self.assertEqual(objective, min_10)

    def test_decode_weekday(self):
        bits = [0, 0, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: ERROR: Weekday is 0.\n"
        self.assertEqual(objective, result)

        bits = [1, 0, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: Weekday: Monday\n"
        self.assertEqual(objective, result)

        bits = [1, 1, 1]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: Weekday: Sunday\n"
        self.assertEqual(objective, result)

        bits = [1, 3, 0]
        result = self.my_decoder.decode_weekday(bits)
        objective = "42-44: ERROR: Weekday is ?.\n"
        self.assertEqual(objective, result)

    def test_decode_day(self):
        bits = [0, 0, 0, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is 00!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        self.assertEqual(objective, day_10)

        bits = [1, 0, 0, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, day_1)
        objective = 0
        self.assertEqual(objective, day_10)

        bits = [0, 0, 0, 0, 1, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, day_1)
        objective = 1
        self.assertEqual(objective, day_10)

        bits = [0, 1, 0, 1, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: 1*digit of day is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = 0
        self.assertEqual(objective, day_10)

        bits = [0, 1, 0, 0, 1, 1]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is > 31!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = "?"
        self.assertEqual(objective, day_10)

        bits = [0, 0, 3, 0, 0, 0]
        [result, day_1, day_10] = self.my_decoder.decode_day(bits)
        objective = "ERROR: Day is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, day_1)
        objective = "?"
        self.assertEqual(objective, day_10)

    def test_decode_month(self):
        bits = [0, 0, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is 00!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        self.assertEqual(objective, month_10)

        bits = [1, 0, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 1
        self.assertEqual(objective, month_1)
        objective = 0
        self.assertEqual(objective, month_10)

        bits = [0, 1, 0, 1, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: 1*digit of month is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = 0
        self.assertEqual(objective, month_10)

        bits = [1, 1, 0, 0, 1]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is > 12!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

        bits = [3, 1, 0, 0, 0]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

        bits = [0, 1, 0, 0, 3]
        [result, month_1, month_10] = self.my_decoder.decode_month(bits)
        objective = "ERROR: Month is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, month_1)
        objective = "?"
        self.assertEqual(objective, month_10)

    def test_decode_year(self):
        bits = [0, 0, 0, 0, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = ""
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, year_1)
        objective = 0
        self.assertEqual(objective, year_10)

        bits = [3, 0, 0, 0, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 0, 0, 0, 0, 0, 0, 3]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is ?.\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 1, 0, 1, 0, 1, 0, 1]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: Year is > 99!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

        bits = [0, 1, 0, 1, 0, 0, 0, 0]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: 1*digit of year is > 9!\n"
        self.assertEqual(objective, result)
        objective = "?"
        self.assertEqual(objective, year_1)
        objective = 0
        self.assertEqual(objective, year_10)

        bits = [0, 0, 0, 0, 0, 1, 0, 1]
        [result, year_1, year_10] = self.my_decoder.decode_year(bits)
        objective = "ERROR: 10*digit of year is > 9!\n"
        self.assertEqual(objective, result)
        objective = 0
        self.assertEqual(objective, year_1)
        objective = "?"
        self.assertEqual(objective, year_10)

    def test_decode_date_weekday(self):
        bits = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "36-41 & 45-57: Date: 01.01.00\n" + \
                    "42-44: Weekday: Monday\n" + \
                    "58: Even parity of date and weekdays successful.\n"
        self.assertEqual(objective, result)

        bits = [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "36-41 & 45-57: Date: 01.01.00\n" + \
                    "42-44: Weekday: Monday\n" + \
                    "58: ERROR: Even parity of date and weekdays failed.\n"
        self.assertEqual(objective, result)

        bits = [3, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "ERROR: Day is ?.\n" + \
                    "36-41 & 45-57: Date: ??.01.00\n" + \
                    "42-44: Weekday: Monday\n" + \
                    "58: ERROR: Even parity of date and weekdays is ?.\n"
        self.assertEqual(objective, result)

        bits = [3, 3, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        result = self.my_decoder.decode_date_weekday(bits)
        objective = "ERROR: Day is ?.\n" + \
                    "36-41 & 45-57: Date: ??.01.00\n" + \
                    "42-44: Weekday: Monday\n" + \
                    "58: ERROR: Even parity of date and weekdays is ?.\n"
        self.assertEqual(objective, result)

        def test_decode_minute_mark(self):
            # positive test - minute mark bit valid (0)
            bit = 0
            result = self.my_decoder.decode_minute_mark(bit)
            objective = "59: Minute mark of DCF77 phase modulation is 0.\n"
            self.assertEqual(objective, result)

            # positive test - minute mark bit valid (1)
            bit = 1
            result = self.my_decoder.decode_minute_mark(bit)
            objective = "59: ERROR: Minute mark of DCF77 phase " + \
                        "modulation failed, it is not 0.\n"
            self.assertEqual(objective, result)
