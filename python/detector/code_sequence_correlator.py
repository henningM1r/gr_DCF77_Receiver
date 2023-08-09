
from gnuradio import gr
import pmt
import numpy as np


class msg_block(gr.basic_block):

    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="Code Sequence \n Correlator",
            in_sig=None,
            out_sig=None)

        # prepare in and out ports for messages
        self.message_port_register_out(pmt.intern('msg_out'))
        self.message_port_register_in(pmt.intern('msg_in'))
        self.set_msg_handler(pmt.intern('msg_in'), self.handle_msg)

        # Both sequences have 256 ones and 256 zeros
        # the spread spectrum codewords for thesymbols 1 and 0
        # are simply bitwise negated versions of each other.
        # LFSR generator polynomial: x^9 + x^5 + 1
        str_known_zero_sequence = "00000100011000010011100101010110000110" \
                                  "11110100110111001000101000010101101001" \
                                  "11111011001001001011011111100100110101" \
                                  "00110011000000011000110010100011010010" \
                                  "11111110100010110001110101100101100111" \
                                  "10001111101110100000110101101101110110" \
                                  "00001011010111110101010100000010100101" \
                                  "01111001011101110000001110011101001001" \
                                  "11101011101010001001000011001110000101" \
                                  "11101101100110100001110111100001111111" \
                                  "11000001111011111000101110011001000001" \
                                  "00101001110110100011110011111001101100" \
                                  "01010100100011100011011010101110001001" \
                                  "100010001000000001"

        str_known_one_sequence = "11111011100111101100011010101001111001" \
                                 "00001011001000110111010111101010010110" \
                                 "00000100110110110100100000011011001010" \
                                 "11001100111111100111001101011100101101" \
                                 "00000001011101001110001010011010011000" \
                                 "01110000010001011111001010010010001001" \
                                 "11110100101000001010101011111101011010" \
                                 "10000110100010001111110001100010110110" \
                                 "00010100010101110110111100110001111010" \
                                 "00010010011001011110001000011110000000" \
                                 "00111110000100000111010001100110111110" \
                                 "11010110001001011100001100000110010011" \
                                 "10101011011100011100100101010001110110" \
                                 "011101110111111110"

        # converting these string of bits to lists with integers
        known_zero_sequence = list(map(int, str_known_zero_sequence))
        known_one_sequence = list(map(int, str_known_one_sequence))

        self.np_knwn_zero_seq = np.array(known_zero_sequence)
        self.np_knwn_one_seq = np.array(known_one_sequence)

        self._min_marker = 0

    def handle_msg(self, msg):
        # message contains whole spread sequence of a received second
        msg = pmt.to_python(msg)
        # print("Message:", msg)

        recv_sequence = list(map(int, msg))
        np_recv_seq = np.array(recv_sequence)

        # extend message at front and at back to
        # have more correlation points in the result
        # NOTE: this seems to be helpful if some bits
        #       are duplicated or lost
        np_recv_seq_padded = np.insert(np_recv_seq, 0, np.zeros(10), axis=0)

        # append zeros before new minute symbol "2"
        if np_recv_seq_padded[-1] == 2:
            np_recv_seq_padded = np.insert(np_recv_seq_padded,
                                           -2, np.zeros(10), axis=0)

        else:    # ordinary case
            np_recv_seq_padded = np.insert(np_recv_seq_padded,
                                           -1, np.zeros(10), axis=0)

        if len(np_recv_seq) > 0:
            res_zero = np.correlate(np_recv_seq_padded, self.np_knwn_zero_seq)
            res_one = np.correlate(np_recv_seq_padded, self.np_knwn_one_seq)
            # print(res_zero)
            # print(res_one)

            # NOTE the max-norm provides good results so far
            norm_zero = max(res_zero)
            norm_one = max(res_one)
            # print("N0: ", norm_zero)
            # print("N1: ", norm_one)

            if norm_zero > norm_one:
                self.message_port_pub(pmt.intern('msg_out'),
                                      pmt.intern('0'))

            elif norm_zero < norm_one:
                self.message_port_pub(pmt.intern('msg_out'),
                                      pmt.intern('1'))

            # even if these norms are identical,
            # an error message might still be useful for the decoder
            # else:
            #    self.message_port_pub(pmt.intern('msg_out'),
            #                          pmt.intern('e'))

            if self._min_marker == 1:
                self.message_port_pub(pmt.intern('msg_out'),
                                      pmt.intern('2'))
                # disable minute marker
                self._min_marker = 0

            # delay minute symbol for a single symbol
            if np_recv_seq[-1] == 2:
                self._min_marker = 1
