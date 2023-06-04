
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):

    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Synchronous\nWaveform Selector',
            in_sig=[np.short,     # selector
                    np.short,     # input signal for symbol zero
                    np.short,     # input signal for symbol one
                    np.short],    # input signal for symbol two
            out_sig=[np.short,    # output signal
                     np.short]    # forward selector
        )

    def work(self, input_items, output_items):
        inp0 = input_items[0]   # selector value
        inp1 = input_items[1]   # input signal for symbol zero
        inp2 = input_items[2]   # input signal for symbol one
        inp3 = input_items[3]   # input signal for symbol two

        # only as initialization value for output signal
        output_items[0][:] = inp3

        # forward the selector value
        output_items[1][:] = inp0

        # synchronously select the input signal to forward it to the output
        output_items[0][:] = self.selsym_to_bbsig(inp0, inp1, inp2, inp3)

        return len(output_items[0])

    # selected symbol to baseband signal
    def selsym_to_bbsig(self, inp0, inp1, inp2, inp3):
        out = inp0

        for idx, ch in enumerate(inp0):
            # forward waveform for symbol zero
            if (ch == 0):
                out[idx] = inp1[idx]

            # forward waveform for symbol one
            elif (ch == 1):
                out[idx] = inp2[idx]

            # forward waveform for symbol two
            elif (ch == 2):
                out[idx] = inp3[idx]

        return out
