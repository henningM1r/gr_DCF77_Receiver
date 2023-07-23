import sys
sys.path.append('..')
from python.decoder import Class_DecodeDCF77_OOK as DCF77
import unittest
from io import StringIO
import zmq
import pmt
import threading
import sys


class Test_Class_DecodeDCF77_OOK(unittest.TestCase):

    def setUp(self):
        self.my_decoder = DCF77.Class_DecodeDCF77_OOK()
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

    def test_decode_startbit(self):
        # positive test - correct start bit
        bit = 0
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: Start-bit is 0.\n"
        self.assertEqual(objective, result)

        # positive test - wrong start bit
        bit = 1
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: Start-bit is 1 instead of 0!\n"
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

    def test_decode_bitstream(self):
        # positive test - too many bits
        bitstream = [0]*60
        result = self.my_decoder.decode_bitstream(bitstream)
        objective = "Decoding error\n#Received bits: 60\n"
        self.assertEqual(objective, result)

        # positive test - too few bits
        bitstream = [0]*58
        result = self.my_decoder.decode_bitstream(bitstream)
        objective = "Decoding error\n#Received bits: 58\n"
        self.assertEqual(objective, result)

        # positive test - valid time
        bitstream = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1,
                     0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0,
                     0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0,
                     0, 1]
        result = self.my_decoder.decode_bitstream(bitstream)
        objective = "\n=== Minute decoded ===\n" \
                    "00: Start-bit is 0.\n" + \
                    "01-14: Weather-info is ignored here.\n" + \
                    "15: Calling bit: 0\n" + \
                    "16: No clock change.\n" + \
                    "17-18: CET - winter time.\n" + \
                    "19: No leap second.\n" + \
                    "20: Begin of time information.\n" + \
                    "28: Even parity of minutes successful.\n" + \
                    "35: Even parity of hours successful.\n" + \
                    "21-27 & 29-34: Time: 17:55h\n" + \
                    "36-41 & 45-57: Date: 11.03.23\n" + \
                    "42-44: Weekday: Saturday\n" + \
                    "58: Even parity of date and weekdays successful.\n" + \
                    "======================"
        self.assertEqual(objective, result)

    def _mock_send_msg(self, msg):
        context = zmq.Context()
        self.socket_sender = context.socket(zmq.PUSH)
        self.socket_sender.bind("tcp://127.0.0.1:55555")
        output = pmt.serialize_str(pmt.to_pmt(msg))
        self.socket_sender.send(output)
        self.socket_sender.close()
        context.term()

    def _mock_send_stream(self, stream, offset=0):
        for i in range(0, len(stream)):
            out_msg = f"{stream[i]}"
            self._mock_send_msg(out_msg)

    def test_consumer(self):
        # positive test - ordinary 0 and 1 at beginning
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run DCF77 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        # send desired messages and exit-signal
        self._mock_send_msg("0")
        self._mock_send_msg("1")
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        objective = "00: 0\n" + \
                    "01: 1\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - ordinary time
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run DCF77 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        bitstream = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1,
                     0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0,
                     0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0,
                     0, 1, 2]
        self._mock_send_stream(stream=bitstream, offset=0)
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        for i in range(0, 60, 1):
            objective += f"{i:02d}: {bitstream[i]}\n"

        objective += "\n=== Minute decoded ===\n" \
                     "00: Start-bit is 0.\n" + \
                     "01-14: Weather-info is ignored here.\n" + \
                     "15: Calling bit: 0\n" + \
                     "16: No clock change.\n" + \
                     "17-18: CET - winter time.\n" + \
                     "19: No leap second.\n" + \
                     "20: Begin of time information.\n" + \
                     "28: Even parity of minutes successful.\n" + \
                     "35: Even parity of hours successful.\n" + \
                     "21-27 & 29-34: Time: 17:55h\n" + \
                     "36-41 & 45-57: Date: 11.03.23\n" + \
                     "42-44: Weekday: Saturday\n" + \
                     "58: Even parity of date and weekdays successful.\n" + \
                     "======================\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder

        # positive test - too many numbers before minute marker
        # Create StringIO object to capture any print-outputs on stdout
        result = StringIO()
        sys.stdout = result

        # run DCF77 decoder in a separate thread and start it
        t_decoder = threading.Thread(target=self.my_decoder.consumer,
                                     name='Thread-consumer')
        t_decoder.start()

        bitstream = [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1,
                     0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0,
                     0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0,
                     0, 1, 0, 2]
        self._mock_send_stream(stream=bitstream, offset=0)
        self._mock_send_msg("___EOT")

        # wait for decoder-thread to be completed
        t_decoder.join()

        objective = ""
        for i in range(0, 61, 1):
            objective += f"{i:02d}: {bitstream[i]}\n"
        objective += "Error: More than 59 bits at new minute\n" + \
                     "#Bits: 60\n"
        self.assertEqual(objective, result.getvalue())

        # full clean-up of decoder
        del t_decoder


if __name__ == '__main__':
    testInstance = Test_Class_DecodeDCF77_OOK()
    unittest.main()
