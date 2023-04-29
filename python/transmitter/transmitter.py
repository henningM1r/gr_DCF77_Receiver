
import numpy as np
from gnuradio import gr
import pmt


"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

# counted number of zero samples
_num_zeros = 0

# counted number of one samples
_num_ones = 0

# counted number of two samples
_num_twos = 0

# counted number of seconds
_num_secs = 0


class blk(gr.sync_block):

    def __init__(self, scaling=1, samp_rate=768000):
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='DCF77-Signalling',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )

        # block parameters
        self.scaling = scaling
        self.sample_rate = samp_rate

        # messaging port
        self.message_port_register_out(pmt.intern('msg_out'))

        # 0.1s of zeros for the zero-bit (100ms pause)
        self._zero = int(self.sample_rate/self.scaling*0.1)

        # 0.9s of ones for the zero-bit
        self._zero_compl = int(self.sample_rate/self.scaling*0.9)

        # 0.2s of zeros for the one-bit (200ms pause)
        self._one = int(self.sample_rate/self.scaling*0.2)

        # 0.8s of ones for the one-bit
        self._one_compl = int(self.sample_rate/self.scaling*0.8)

        # 1.9s of ones for the zero-bit at position 58 (with prolonged ones)
        self._reinit_zero = int(self.sample_rate/self.scaling*1.9)

        # 1.8s of ones for the one-bit at position 58 (with prolonged ones)
        self._reinit_one = int(self.sample_rate/self.scaling*1.8)

        print("zero:", self._zero)
        print("zero_compl:", self._zero_compl)
        print("one:", self._one)
        print("one_compl:", self._one_compl)
        print("reinit_zero:", self._reinit_zero)
        print("reinit_one:", self._reinit_one)

    def work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]

        # tags = self.get_tags_in_window(0, 0, len(inp))

        out[:] = self.bits_to_base_band_signal(inp)

        # forward input tagged signal
        return len(output_items[0])

    def bits_to_base_band_signal(self, inp):
        global _num_zeros
        global _num_ones
        global _num_twos
        global _num_secs

        # The total number of samples does not change from input to output
        # just the value might change
        out = inp

        # tags = self.get_tags_in_window(0, 0, len(inp))

        # Process the individual (finite length) stream block currently
        # received. Either a frame (sample_rate) full of ones, or a frame
        # full of zeros is received.
        for idx, ch in enumerate(inp):
            # 1 is default, especially for the 59th second
            out[idx] = 1

            if _num_secs > 59:
                _num_secs = 0

            # receiving frame of zeros
            if (ch == 0):
                _num_zeros += 1
                _num_ones = 0
                _num_twos = 0

                # if the number of zeros is below 0.1s of the frame
                if (_num_zeros < self._zero and
                        _num_secs < 59):
                    # set the output to "1" for the current sample
                    out[idx] = 0

                # if the number of zeros is equal 0.1s of the frame
                elif (_num_zeros == self._zero and
                      _num_secs < 59):
                    # set output to "0" for the current sample
                    out[idx] = 0

                    # set tag for this 100ms pause
                    key = pmt.intern("0")
                    value = pmt.intern("100ms")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

                # if the number of zeros is above 0.1s of the frame
                elif (_num_zeros > self._zero and
                      _num_secs < 59):
                    # set output to "1" for the current sample
                    out[idx] = 1

                # full second from a full frame of zeros
                if _num_zeros >= self.sample_rate:
                    _num_zeros = 0
                    _num_ones = 0
                    _num_twos = 0
                    _num_secs += 1

                    if _num_secs < 59:
                        # set tag for full second
                        key = pmt.intern("sec")
                        value = pmt.intern("0")
                        self.add_item_tag(0,
                                          self.nitems_written(0) + idx,
                                          key,
                                          value)

                    print(f"{_num_secs:02d}: 0")

            # receiving frame of ones
            elif (ch == 1):
                _num_ones += 1
                _num_zeros = 0
                _num_twos = 0

                # if the number of ones is below 0.2s of the frame
                if (_num_ones < self._one and
                        _num_secs < 59):
                    # set the output to "0" for the current sample
                    out[idx] = 0

                # if the number of ones is equal 0.2s of the frame
                elif (_num_ones == self._one and
                      _num_secs < 59):
                    # set output to "0" for the current sample
                    out[idx] = 0
                    # set tag for this 200ms pause
                    key = pmt.intern("1")
                    value = pmt.intern("200ms")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

                # if the number of ones is above 0.2s of the frame
                elif (_num_ones > self._one and _num_secs < 59):
                    # set output to "1" for the current sample
                    out[idx] = 1

                # full second from a full frame of ones
                if _num_ones >= self.sample_rate:
                    _num_ones = 0
                    _num_zeros = 0
                    _num_twos = 0
                    _num_secs += 1

                    if _num_secs < 59:
                        # set tag for full second
                        key = pmt.intern("sec")
                        value = pmt.intern("1")
                        self.add_item_tag(0,
                                          self.nitems_written(0) + idx,
                                          key,
                                          value)

                    print(f"{_num_secs:02d}: 1")

            # receiving frame of twos (=> 59th second)
            elif (ch == 2):
                _num_zeros = 0
                _num_ones = 0

                if _num_twos == 0:
                    _num_secs += 1
                    _num_twos += 1

                    out[idx] = 1

                    print(f"{_num_secs:02d}: _")

                elif _num_twos >= 1 and _num_twos < self.sample_rate:
                    _num_twos += 1

                    out[idx] = 1

                elif _num_twos >= self.sample_rate:
                    _num_twos = 0

                    out[idx] = 1

        # return (float) signal block
        return out
