
import sys
import time

import numpy as np
from gnuradio import gr, gr_unittest
from gnuradio import blocks
import pmt

sys.path.append('..')
from examples.DCF77_Receiver \
    import DCF77_Receiver_PhaseMod_epy_block_0 \
    as DCF77_BitDetector_PhaseMod
import msg_test_block


class test_gr_bitDetector_PhaseMod(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def setUp_Block(self):
        # NOTE the vector is just simple default
        # value for the instantiation
        vin = np.zeros(1)
        vin2 = vin.tolist()

        self.src_sig_magn = blocks.vector_source_f(vin2, False)
        self.src_sig_phase = blocks.vector_source_f(vin2, False)
        self.snk_sig = blocks.vector_sink_f(1)
        self.snk_msg = msg_test_block.msg_receiver_test_block()

        # NOTE the test_block must be instantiated and run once
        #      before a subroutines is called manually
        self.test_block = (DCF77_BitDetector_PhaseMod.DCF77_BitDetector_blk(
            sample_rate=48000, chip_size=75, debug=True))

        self.tb.connect(self.src_sig_magn, (self.test_block, 0))
        self.tb.connect(self.src_sig_phase, (self.test_block, 1))
        self.tb.connect((self.test_block, 0), self.snk_sig)
        self.tb.msg_connect((self.test_block, 'msg_out'),
                            (self.snk_msg, 'msg_in'))

        self.tb.run()
        self.test_block.reinit_code()

    def tearDown(self):
        # return to initial state
        DCF77_BitDetector_PhaseMod._in_sync = 0
        DCF77_BitDetector_PhaseMod._num_ones = 0
        DCF77_BitDetector_PhaseMod._num_zeros = 0
        DCF77_BitDetector_PhaseMod._code = np.array([])

        self.tb = None

    def test_gr_work(self):
        self.setUp_Block()

        # NOTE this call actually shows up
        # in the unittest coverage
        vin = np.zeros(2)
        vin = np.append(vin, np.ones(2))
        vin = np.append(vin, np.zeros(2))
        vin2 = vin.tolist()
        vin_magn = np.ones(6).tolist()

        vout = [vin.copy().tolist()]
        result = self.test_block.work(input_items=[vin2.copy(), vin_magn.copy()],
                                      output_items=vout)
        self.tb.stop()

        # TODO objective, result and assertions missing
        del self.test_block
        self.tearDown()

    def test_code_append(self):
        self.setUp_Block()

        objective = [1]
        result = list(self.test_block.code_append(code=[], num=75, mode=+1))
        self.assertEqual(objective, result)

        objective = [0]
        result = list(self.test_block.code_append(code=[], num=75, mode=-1))
        self.assertEqual(objective, result)

        objective = [2]
        result = list(self.test_block.code_append(code=[], num=75, mode=+2))
        self.assertEqual(objective, result)

        objective = [0, 1, 0, 1]
        result = list(self.test_block.code_append(code=[0, 1, 0],
                                                  num=75, mode=+1))
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()

    def test_transmit_code(self):
        self.setUp_Block()

        code = np.array([1])
        self.test_block.transmit_code(code)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("1")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        self.test_block.reinit_code()

        code = np.array([0])
        self.test_block.transmit_code(code)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("0")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        self.test_block.reinit_code()

        code = np.array([1, 0, 1, 1, 0, 0, 1])
        self.test_block.transmit_code(code)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("1011001")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()

    def test_reinit_code(self):
        self.setUp_Block()

        DCF77_BitDetector_PhaseMod._num_pos = 3
        DCF77_BitDetector_PhaseMod._num_neg = 4

        self.test_block.reinit_code()

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_pos
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_neg
        self.assertEqual(objective, result)

        objective = []
        result = DCF77_BitDetector_PhaseMod._code.tolist()
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()

    """def test_edge_detection_p1(self):
        self.setUp_Block()

        # 1-symbol
        vin = np.ones(75)
        vin = np.append(vin, -np.ones(1))
        vin = np.append(vin, np.zeros(1))
        vin2 = vin.tolist()
        vin_magn = np.ones(77).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("1")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        objective = []
        result = DCF77_BitDetector_PhaseMod._code.tolist()
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_pos
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_neg
        self.assertEqual(objective, result)

        self.test_block.reinit_code()

        # 2x 1-symbol
        vin = np.ones(150)
        vin = np.append(vin, -np.ones(1))
        vin = np.append(vin, np.zeros(1))
        vin2 = vin.tolist()
        vin_magn = np.ones(152).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("11")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        objective = []
        result = DCF77_BitDetector_PhaseMod._code.tolist()
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_pos
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_neg
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()

    def test_gr_edge_detection_m1(self):
        self.setUp_Block()

        # 0-symbol
        vin = -np.ones(75)
        vin = np.append(vin, np.ones(1))
        vin = np.append(vin, np.zeros(1))
        vin2 = vin.tolist()
        vin_magn = np.ones(77).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("0")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        objective = []
        result = DCF77_BitDetector_PhaseMod._code.tolist()
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_pos
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_neg
        self.assertEqual(objective, result)

        self.test_block.reinit_code()

        # 2x 0-symbol
        vin = -np.ones(150)
        vin = np.append(vin, np.ones(1))
        vin = np.append(vin, np.zeros(1))
        vin2 = vin.tolist()
        vin_magn = np.ones(152).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("00")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        objective = []
        result = DCF77_BitDetector_PhaseMod._code.tolist()
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_pos
        self.assertEqual(objective, result)

        objective = 0
        result = DCF77_BitDetector_PhaseMod._num_neg
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()

    def test_gr_bitDetector_2(self):
        self.setUp_Block()

        vin = np.ones(9504)
        vin2 = vin.tolist()
        vin_magn = np.ones(9504).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("2")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        self.test_block.reinit_code()

        vin = -np.ones(9504)
        vin2 = vin.tolist()
        vin_magn = np.ones(9504).tolist()

        self.test_block.edge_detection(vin2, vin_magn)

        self.tb.start()
        time.sleep(0.1)
        self.tb.stop()
        self.tb.wait()

        objective = pmt.intern("2")
        result = self.snk_msg.get_msg()
        self.assertEqual(objective, result)

        del self.test_block
        self.tearDown()"""


if __name__ == '__main__':
    gr_unittest.run(test_gr_bitDetector_PhaseMod.test_gr_work())
    gr_unittest.run(test_gr_bitDetector_PhaseMod.test_code_append())
    gr_unittest.run(test_gr_bitDetector_PhaseMod.test_transmit_code())
    gr_unittest.run(test_gr_bitDetector_PhaseMod.test_reinit_code())
    #gr_unittest.run(test_gr_bitDetector_PhaseMod.test_edge_detection_p1())
    #gr_unittest.run(test_gr_bitDetector_PhaseMod.test_edge_detection_m1())
    #gr_unittest.run(test_gr_bitDetector_PhaseMod.test_gr_bitDetector_2())
