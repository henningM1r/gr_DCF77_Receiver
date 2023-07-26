# -*- coding: iso-8859-1 -*-

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

    def test_decode_startbit(self):
        # positive test - correct start bit
        bit = 0
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: Start-bit is 0.\n"
        self.assertEqual(objective, result)

        # positive test - wrong start bit
        bit = 1
        result = self.my_decoder.decode_startbit(bit)
        objective = "00: ERROR: Start-bit is 1 instead of 0!\n"
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
