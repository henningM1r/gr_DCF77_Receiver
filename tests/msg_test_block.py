
from gnuradio import gr
import pmt


# https://www.gnuradio.org/doc/doxygen-v3.7.10/page_python_blocks.html#pyblocks_msgs
class msg_receiver_test_block(gr.basic_block):

    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="msg_test_block",
            in_sig=None,
            out_sig=None)
        self.message_port_register_in(pmt.intern('msg_in'))
        self.set_msg_handler(pmt.intern('msg_in'), self.handle_msg)

        self.cur_msg = None

    def handle_msg(self, msg):
        self.cur_msg = msg

    def get_msg(self):
        return self.cur_msg
