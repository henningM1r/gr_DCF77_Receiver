
import numpy as np
from gnuradio import gr
import pmt


# counted number of +1 samples
_num_pos = 0
# counted number of -1 samples
_num_neg = 0
# counted number of zero samples
_num_zero = 0

# array for each chip symbol per second
_code = []
_code = np.array(_code)


class blk(gr.sync_block):

    def __init__(self, samp_rate=48000, chip_size=75):

        gr.sync_block.__init__(
            self,
            name='DCF77\nPhase Detector',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )

        self.samp_rate = samp_rate
        self.off_duration = int(self.samp_rate*0.3)

        # from signal inspection: size between approx. 74-78 seems good
        self.chip_size = chip_size

        self.message_port_register_out(pmt.intern('msg_out'))

        print("Edge Tagger")
        print("samp_rate:", self.samp_rate)
        print("off_duration:", self.off_duration)

    def work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]

        out[:] = self.edge_detection(inp)

        return len(out)

    def code_append(self, code, num, mode):
        # estimated number of +1/-1 for given chip_size
        # NOTE: rounding provides much better results than just int
        _num_bits = int(round(num/self.chip_size))

        if mode == +1:
            res = np.append(code, np.ones(_num_bits))
        elif mode == -1:
            res = np.append(code, np.zeros(_num_bits))
        elif mode == 2:
            res = np.append(code, 2)

        return res

    def transmit_code(self, code):
        # convert list to a sequence of bits
        code = code.astype(int).tolist()
        msg = "".join(str(x) for x in code)

        self.message_port_pub(pmt.intern("msg_out"),
                              pmt.intern(f"{msg}"))

    def reinit_code(self):
        global _code
        global _num_pos
        global _num_neg

        # reinitialize code vector
        _code = []
        _code = np.array(_code)

        _num_pos = 0
        _num_neg = 0

    def edge_detection(self, inp):
        global _num_pos
        global _num_neg
        global _num_zero
        global _code

        out = inp
        
        for idx, ch in enumerate(inp):
            if (ch == +1):
                _num_pos += 1
            
            elif (ch == -1):
                _num_neg += 1

            else:   # ch == 0
                _num_pos = 0
                _num_neg = 0  
                _num_zero += 1

            # ensure the total break is always 200ms
            # NOTE: there might be a more elegant solution,
            # but it works for now.
            if (_num_zero > 1 and
                    _num_zero < self.off_duration):
                _num_pos = 0
                _num_neg = 0
                _num_zero += 1
                out[idx] = 0

            # Detect the minute marker within the phase signal:
            # The minute marker has a prolonged high OOK signal. In the phase
            # signal there are two symbols contained with a 200ms break in
            # between. Thus the break is either a long 1 or long -1 instead of
            # a (muted) zero. This longer +/-1 symbol trigggers the minute
            # detector. Note that the very next symbol yet belongs to the
            # current minute. Further suqbsequent symbols belong to the next
            # minute as expected!
            if (_num_pos > int(self.off_duration*0.66) or
                    _num_neg > int(self.off_duration*0.66)):
                key = pmt.intern("e")
                value = pmt.intern("2")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                _code = self.code_append(code=_code, num=1, mode=2)

                self.transmit_code(code=_code)
                self.reinit_code()

            # detect edge from +1 -> -1
            elif _num_pos > 1 and ch == -1:
                key = pmt.intern("e")
                value = pmt.intern(f"-1, {_num_pos}")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                _code = self.code_append(code=_code, num=_num_pos, mode=+1)

                _num_pos = 0
                _num_zero = 0

            # detect edge from -1 -> +1
            elif _num_neg > 1 and ch == +1:
                key = pmt.intern("e")
                value = pmt.intern(f"+1, {_num_neg}")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                _code = self.code_append(code=_code, num=_num_neg, mode=-1)

                _num_neg = 0
                _num_zero = 0

            # detect edge from 0 -> +1
            elif (_num_zero > 1 and
                    _num_zero >= self.off_duration and
                    ch == +1):
                key = pmt.intern("e")
                value = pmt.intern("+1")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                _num_neg = 0
                _num_zero = 0

            # detect edge from 0 -> -1
            elif (_num_zero > 1 and
                    _num_zero >= self.off_duration and
                    ch == -1):
                key = pmt.intern("e")
                value = pmt.intern("-1")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                _num_pos = 0
                _num_zero = 0

            # detect edge from -1 -> 0
            elif _num_zero == 1:
                key = pmt.intern("e")
                value = pmt.intern("0")
                self.add_item_tag(0,
                    self.nitems_written(0) + idx,
                    key,
                    value)

                self.transmit_code(code=_code)
                self.reinit_code()

        return out

            

