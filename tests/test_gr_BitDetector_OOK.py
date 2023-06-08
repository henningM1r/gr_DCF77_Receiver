
import sys
sys.path.append('..')
from examples.DCF77_Receiver import DCF77_Receiver_OOK_gr_bit_detector_DCF77 as DCF77_BitDetector_OOK
import numpy
from gnuradio import gr, gr_unittest
from gnuradio import blocks


class test_gr_bitDetector(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def setUp_Block(self):
        # NOTE the vector is just simple default value for the instantiation
        vin = numpy.zeros(1)
        vin2 = vin.tolist()

        src_sig = blocks.vector_source_f(vin2, False)
        snk_sig = blocks.vector_sink_f(1)
        snk_msg = blocks.message_debug()

        # NOTE the test_block must be instantiated and run once
        #      before a subroutines is called manually
        self.test_block = DCF77_BitDetector_OOK.DCF77_BitDetector_blk(
            sample_rate=48000, tolerance=0.02)

        self.tb.connect(src_sig, (self.test_block, 0))
        self.tb.connect((self.test_block, 0), snk_sig)
        self.tb.run()

    def tearDown(self):
        # return to initial state
        DCF77_BitDetector_OOK._in_sync = 0
        DCF77_BitDetector_OOK._num_ones = 0
        DCF77_BitDetector_OOK._num_zeros = 0

        self.tb = None

    """
    def test_gr_bitDetector_default(self):
        # construct a valid binary input signal
        vin = numpy.zeros(10)
        vin = vin.tolist()

        # signal source
        src_sig = blocks.vector_source_f(vin, False)

        # block to test
        test_block = DCF77_BitDetector_OOK.DCF77_BitDetector_blk(sample_rate=48000, tolerance=0.02)

        # signal and message sinks
        snk_sig = blocks.vector_sink_f(1)
        snk_msg = blocks.message_debug()

        self.tb.connect(src_sig, (test_block, 0))
        self.tb.connect((test_block, 0), snk_sig)
        self.tb.msg_connect((test_block, 'msg_out'), (snk_msg, 'print'))
        self.tb.run()

        ## check default parameters of block
        # check default sample_rate
        objective = 48000
        result = test_block.sample_rate
        self.assertEqual(objective, result)

        # check default tolerance
        objective = 0.02
        result = test_block.tolerance
        self.assertEqual(objective, result)

        # check default zero_lo
        objective = 3840.0
        result = test_block._zero_lo
        self.assertEqual(objective, result)

        # check default zero_hi
        objective = 5760.0
        result = test_block._zero_hi
        self.assertEqual(objective, result)

        # check default one_lo
        objective = 8640.0
        result = test_block._one_lo
        self.assertEqual(objective, result)

        # check default one_hi
        objective = 10560.0
        result = test_block._one_hi
        self.assertEqual(objective, result)

        # check signal output
        vout = numpy.zeros(10).tolist()
        objective = vout
        result = snk_sig.data()
        self.assertEqual(objective, result)

        # check message output
        objective = 0
        result = snk_msg.num_messages()
        self.assertEqual(objective, result)

    def test_gr_bitDetector_0(self):
        # construct a valid binary input signal
        # first sync
        vin = numpy.zeros(4800)
        vin = numpy.append(vin, numpy.ones(43200))

        ## 0-symbol
        vin = numpy.append(vin, numpy.zeros(4800))
        vin = numpy.append(vin, numpy.ones(43200))
        vin = vin.tolist()

        # signal source
        src_sig = blocks.vector_source_f(vin, False)

        # block to test
        test_block = DCF77_BitDetector_OOK.DCF77_BitDetector_blk(sample_rate=48000, tolerance=0.02)

        # signal and message sinks
        snk_sig = blocks.vector_sink_f(1)
        snk_msg = blocks.message_debug()

        self.tb.connect(src_sig, (test_block, 0))
        self.tb.connect((test_block, 0), snk_sig)
        self.tb.msg_connect((test_block, 'msg_out'), (snk_msg, 'print'))

        #self.tb.run()
        self.tb.start()
        #self.waitFor(lambda: snk_msg.num_messages() >= 1, timeout=2.0, poll_interval=0.01)
        self.tb.stop()
        self.tb.wait()

        # check signal output
        #vout = numpy.zeros(4800).tolist()
        #objective = vout
        #result = snk_sig.data()
        #self.assertEqual(objective, result)

        # check message output
        objective = 0
        result = snk_msg.num_messages()
        self.assertEqual(objective, result)

    def test_gr_bitDetector_1(self):
        # construct a valid binary input signal
        # first sync
        vin = numpy.zeros(1)
        vin = numpy.append(vin, numpy.ones(43200))

        ## 1-symbol
        vin = numpy.append(vin, numpy.zeros(9600))
        vin = numpy.append(vin, numpy.ones(38400))

        vin = vin.tolist()

        # signal source
        src_sig = blocks.vector_source_f(vin, False)

        # block to test
        test_block = DCF77_BitDetector_OOK.DCF77_BitDetector_blk(sample_rate=48000, tolerance=0.02)

        # signal and message sinks
        snk_sig = blocks.vector_sink_f(1)
        snk_msg = blocks.message_debug()

        self.tb.connect(src_sig, (test_block, 0))
        self.tb.connect((test_block, 0), snk_sig)
        self.tb.msg_connect((test_block, 'msg_out'), (snk_msg, 'print'))

        self.tb.start()
        #self.waitFor(lambda: snk_msg.num_messages() == 1, timeout=1.0, poll_interval=0.01)
        self.tb.stop()
        self.tb.wait()

        # check signal output
        #vout = numpy.zeros(4800).tolist()
        #objective = vout
        #result = snk_sig.data()
        #self.assertEqual(objective, result)

        # check message output
        #objective = "0"
        #result = snk_msg.get_message(0)
        #self.assertEqual(objective, result)
"""
    def test_gr_work(self):
        self.setUp_Block()

        # NOTE this call actually shows up in the unittest coverage
        vin = numpy.zeros(2)
        vin = numpy.append(vin, numpy.ones(2))
        vin = numpy.append(vin, numpy.zeros(2))
        vin2 = vin.tolist()

        vout = [vin.copy().tolist()]
        result = self.test_block.work(input_items=[vin2.copy()], output_items=vout)
        self.tb.stop()

        del self.test_block
        self.tearDown()

    def test_gr_sync_s0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # stay in status 0
        vin = numpy.ones(1)
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_sm1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 0 to status -1
        vin = numpy.append(numpy.ones(1), numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = -1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_sm2_0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -1 to status -2
        DCF77_BitDetector_OOK._in_sync = -1
        vin = numpy.zeros(3841)
        vin = numpy.append(vin, numpy.ones(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = -2
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_sm2_1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -1 to status -2
        DCF77_BitDetector_OOK._in_sync = -1
        vin = numpy.zeros(8641)
        vin = numpy.append(vin, numpy.ones(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = -2
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s1_0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -2 to status 1
        DCF77_BitDetector_OOK._in_sync = -2
        vin = numpy.ones(42241)
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s1_1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -2 to status 1
        DCF77_BitDetector_OOK._in_sync = -2
        vin = numpy.ones(37441)
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s1_0neg(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -2 to status 1
        DCF77_BitDetector_OOK._in_sync = -2
        vin = numpy.ones(42240)
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = -1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s1_1neg(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status -2 to status -1
        DCF77_BitDetector_OOK._in_sync = -2
        vin = numpy.ones(37440)
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = -1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s2_0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 1 to status 2
        DCF77_BitDetector_OOK._in_sync = 1
        vin = numpy.zeros(3840)
        vin = numpy.append(vin, numpy.ones(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 2
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_s2_1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 1 to status 2
        DCF77_BitDetector_OOK._in_sync = 1
        vin = numpy.zeros(8640)
        vin = numpy.append(vin, numpy.ones(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 2
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_bit_0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 2
        vin = numpy.zeros(3840)
        vin = numpy.append(vin, numpy.ones(42241))
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_bit_1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 2
        vin = numpy.zeros(8640)
        vin = numpy.append(vin, numpy.ones(37441))
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_NewMin_0(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 2
        vin = numpy.zeros(3840)
        vin = numpy.append(vin, numpy.ones(89281))
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_newMin_1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 2
        vin = numpy.zeros(8640)
        vin = numpy.append(vin, numpy.ones(84481))
        vin = numpy.append(vin, numpy.zeros(1))
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 1
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_lost_sm1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = -1
        vin = numpy.zeros(21120)
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_lost_s1(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 1
        vin = numpy.zeros(21120)
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

    def test_gr_sync_lost_s2(self):
        # yet unsynchronized
        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        self.setUp_Block()

        # (minimal example) go from status 2 to status 1
        DCF77_BitDetector_OOK._in_sync = 2
        vin = numpy.zeros(21120)
        vin2 = vin.tolist()

        result = self.test_block.extract_bits(inp=vin2)

        objective = 0
        result = DCF77_BitDetector_OOK._in_sync
        self.assertEqual(objective, result)

        del self.test_block

if __name__ == '__main__':
    gr_unittest.run(test_gr_bitDetector.test_gr_bitDetector_default, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_bitDetector_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_bitDetector_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_work, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_sm1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_sm2_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_sm2_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s1_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s1_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s1_0neg, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s1_1neg, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s2_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_s2_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_bit_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_bit_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_NewMin_0, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_NewMin_1, "test_gr_BitDetector_OOK.xml")
    gr_unittest.run(test_gr_bitDetector.test_gr_sync_lost_0, "test_gr_BitDetector_OOK.xml")

    # TBD test_gr_sync_lost_sm2