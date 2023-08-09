
import numpy as np
from gnuradio import gr
import pmt


# the DCF77 detector is initially out of sync
_in_sync = 0
# counted number of one samples
_num_ones = 0
# counted number of zero samples
_num_zeros = 0


class DCF77_BitDetector_blk(gr.sync_block):

    def __init__(self, sample_rate=48000, tolerance=0.02):
        gr.sync_block.__init__(
            self,
            name='DCF77\nBit Detector',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )

        # block paramters
        # NOTE: use decimated sample rate: samp_rate/decimation
        self.sample_rate = sample_rate
        self.tolerance = tolerance

        # messaging port
        self.message_port_register_out(pmt.intern('msg_out'))

        # timing tolerance value, if the sampled frame is
        # slightly shorter/longer hant the defined duration
        self._tolerance = self.sample_rate*self.tolerance

        # 0.1s of zeros for the zero-bit (100ms pause)
        self._zero_lo = self.sample_rate*0.1 - self._tolerance
        self._zero_hi = self.sample_rate*0.1 + self._tolerance

        # 0.9s of ones for the zero-bit
        self._zero_compl_lo = self.sample_rate*0.9 - self._tolerance
        self._zero_compl_hi = self.sample_rate*0.9 + self._tolerance

        # 0.2s of zeros for the one-bit (200ms pause)
        self._one_lo = self.sample_rate*0.2 - self._tolerance
        self._one_hi = self.sample_rate*0.2 + self._tolerance

        # 0.8s of ones for the one-bit
        self._one_compl_lo = self.sample_rate*0.8 - self._tolerance
        self._one_compl_hi = self.sample_rate*0.8 + self._tolerance

        # 1.9s of ones for the zero-bit at position 58 (with prolonged ones)
        self._reinit_zero_lo = self.sample_rate*1.9 - 2*self._tolerance
        self._reinit_zero_hi = self.sample_rate*1.9 + 2*self._tolerance

        # 1.8s of ones for the one-bit at position 58 (with prolonged ones)
        self._reinit_one_lo = self.sample_rate*1.8 - 2*self._tolerance
        self._reinit_one_hi = self.sample_rate*1.8 + 2*self._tolerance

        print("zero", (self._zero_hi + self._zero_lo)/2)
        print("zero_comp", (self._zero_compl_hi + self._zero_compl_lo)/2)
        print("one", (self._one_hi + self._one_lo)/2)
        print("one_comp", (self._one_compl_hi + self._one_compl_lo)/2)
        print("zero_reinit", (self._reinit_zero_hi + self._reinit_zero_lo)/2)
        print("one_reinit", (self._reinit_one_hi + self._reinit_one_lo)/2)

    def work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]

        out[:] = self.extract_bits(inp)

        # forward input tagged signal
        return len(out)

    def extract_bits(self, inp):
        global _in_sync
        global _num_ones
        global _num_zeros

        out = inp

        # Process the individual (finite length) stream block
        # currently received. The synchronization and detection process
        # is basically modelled by a finite state. machine
        for idx, ch in enumerate(inp):
            # increment current counters of zeros and ones correspondingly
            if (ch == 1):
                _num_ones += 1
            else:   # ch == 0
                _num_zeros += 1

            # first step of synchronization,
            # as soon as an edge
            # from zero to one is detected
            if (_in_sync == 0 and ch == 0):
                _in_sync = -1
                _num_zeros = 1
                _num_ones = 0

                key = pmt.intern("")
                value = pmt.intern(f"0 => -1 {_num_zeros}, {_num_ones}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

            # do not (yet) synchronize if there
            # is no edge from zero to one yet
            elif (_in_sync == 0 and ch == 1):
                # thus keep _in_sync_ = 0
                pass

            # second step of synchronization succeeds,
            # as soon as an edge from one to zero is
            # detected during state -1, given that the
            # length of zeros fits to parts of the
            # zero/one symbols correspondingly
            if (_in_sync == -1 and ch == 1 and
                    ((_num_zeros > self._zero_lo and
                      _num_zeros < self._zero_hi) or
                     (_num_zeros > self._one_lo and
                      _num_zeros < self._one_hi))):
                _in_sync = -2
                _num_zeros = 0
                _num_ones = 1

                key = pmt.intern("")
                value = pmt.intern(f"-1 => -2  {_num_zeros}, {_num_ones}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

            # second step of synchronization fails otherwise
            elif (_in_sync == -1 and ch == 1 and
                    (_num_zeros < self._zero_lo or
                     _num_zeros > self._one_hi)):
                _in_sync = 0

                key = pmt.intern("")
                value = pmt.intern(f"ERR: -1 => 0: {_num_zeros}, {_num_ones}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)
                _num_zeros = 0
                _num_ones = 1

            # do not (yet) synchronize if there
            # is no edge from zero to one yet
            elif (_in_sync == -1 and ch == 0):
                pass

            # third (and last) step of synchronization succeeds,
            # as soon as an edge from one to zero is
            # detected during state -2, given that the
            # length of ones fits to parts of the
            # zero/one symbols correspondingly
            if (_in_sync == -2 and ch == 0 and
                    ((_num_ones > self._zero_compl_lo and
                      _num_ones < self._zero_compl_hi) or
                     (_num_ones > self._one_compl_lo and
                      _num_ones < self._one_compl_hi))):
                _in_sync = 1
                _num_zeros = 1
                _num_ones = 0

                key = pmt.intern("")
                value = pmt.intern("-2 => 1")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

            # third (and last) step of synchronization fails otherwise
            elif (_in_sync == -2 and ch == 0 and
                    ((_num_ones < self._zero_compl_lo or
                      _num_ones > self._one_compl_hi) or
                     (_num_ones > self._zero_compl_hi and
                      _num_ones < self._one_compl_lo))):
                _in_sync = -1
                _num_zeros = 1
                _num_ones = 0

                key = pmt.intern("")
                value = pmt.intern(f"ERR: -2 => -1: {_num_zeros}, {_num_ones}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

            # do not (yet) synchronize if there
            # is no edge from one to zero yet
            elif (_in_sync == -2 and ch == 1):
                pass

            # sync on rising edge is successful
            # so far it is either a zero or a one symbol
            if (_in_sync == 1 and ch == 1 and
                    ((_num_zeros > self._zero_lo and
                      _num_zeros < self._zero_hi) or
                     (_num_zeros > self._one_lo and
                      _num_zeros < self._one_hi))):
                _in_sync = 2
                _num_ones = 1

                key = pmt.intern("")
                value = pmt.intern(f"1 => 2 {_num_zeros}, {_num_ones}")
                self.add_item_tag(0,
                                  self.nitems_written(0) + idx,
                                  key,
                                  value)

            # detect zero bit on falling edge at each end of the symbol frame
            if (_in_sync == 2 and ch == 0):

                # detect a zero bit, if approx 0.1sec zeros and 0.9sec ones
                # (in that order) with slight tolerances are detected
                if (_num_zeros > self._zero_lo and
                        _num_zeros < self._zero_hi and
                        _num_ones > self._zero_compl_lo and
                        _num_ones < self._zero_compl_hi):

                    # reset counters to zero
                    _num_ones = 0
                    _num_zeros = 1

                    _in_sync = 1

                    key = pmt.intern("")
                    value = pmt.intern("2 => 1: BIT ZERO")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

                    # detected 0 bit
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern("0"))

                # detect a one bit, if approx 0.2sec zeros and 0.8sec ones
                # (in that order) with slight tolerances are detected
                elif (_num_zeros > self._one_lo and
                      _num_zeros < self._one_hi and
                      _num_ones > self._one_compl_lo and
                      _num_ones < self._one_compl_hi):

                    # reset counters to zero
                    _num_ones = 0
                    _num_zeros = 1

                    _in_sync = 1

                    key = pmt.intern("")
                    value = pmt.intern("2 => 1: BIT ONE")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

                    # detected 0 bit
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern("1"))

                # detect a zero bit and a new minute, if approx 0.1sec
                # zeros and 1.9sec ones (in that order) with slight
                # tolerances are detected
                elif (_num_zeros > self._zero_lo and
                      _num_zeros < self._zero_hi and
                      _num_ones > self._reinit_zero_lo and
                      _num_ones < self._reinit_zero_hi):

                    # detected 0 bit
                    msg = "0"
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern(msg))

                    # detected new minute
                    msg = "2"
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern(msg))
                    # reset counters to zero
                    _num_ones = 0
                    _num_zeros = 1

                    _in_sync = 1

                    key = pmt.intern("")
                    value = pmt.intern("2 => 1: NEW MIN")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

                # detect a one bit and a new minute, if approx 0.2sec
                # zeros and 1.8sec ones (in that order) with slight
                # tolerances are detected
                elif (_num_zeros > self._one_lo and
                      _num_zeros < self._one_hi and
                      _num_ones > self._reinit_one_lo and
                      _num_ones < self._reinit_one_hi):

                    # detected one bit
                    msg = "1"
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern(msg))

                    # detected new minute
                    msg = "2"
                    self.message_port_pub(pmt.intern("msg_out"),
                                          pmt.intern(msg))

                    # reset counters to zero
                    _num_ones = 0
                    _num_zeros = 1

                    _in_sync = 1

                    key = pmt.intern("")
                    value = pmt.intern("2 => 1: NEW MIN")
                    self.add_item_tag(0,
                                      self.nitems_written(0) + idx,
                                      key,
                                      value)

            elif (_in_sync == 2 and ch == 1):
                pass

        # detect and treat the case when sync is apparently lost
        # and the counters start to overload
        if (_num_zeros > self._one_hi*2 or
                _num_zeros > self._reinit_one_hi*2):
            msg = "ERROR"
            self.message_port_pub(pmt.intern("msg_out"),
                                  pmt.intern(f"({msg}), zeros:"
                                             f"{_num_zeros},"
                                             f" ones: {_num_ones}"))

            # trigger a re-sync
            _in_sync = 0

            # reset all counters to zero
            _num_ones = 0
            _num_zeros = 1

            key = pmt.intern("")
            value = pmt.intern("2 => -1: ERROR")
            self.add_item_tag(0,
                              self.nitems_written(0) + idx,
                              key,
                              value)

        # return (float) signal block
        return out
