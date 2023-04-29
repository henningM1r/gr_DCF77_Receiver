# -*- coding: iso-8859-1 -*-

##
# input:
# * get time information from datetime library (implemented)
#
# output:
# * provide DCF77 bit-vector of a full-minute (60 bits)
# * provide bit-vector with the beginning of each minute
# * Note that the "next" minute is provided, not the "current" one
#
# tests:
# * generated DCF77 bit-vector from the Encoder must be decodable by
#   the DCF77 decoder and resemble the identical time
##


from datetime import datetime, timedelta
import time
import zmq
import pytz
import numpy as np


class DCF77Encoder():

    def __init__(self, tcp_addr="127.0.0.1", port=55552):
        # provide bit-stream via ZMQ_PUB as client to server
        # simulated RF-transmission in GNURadio

        # usually the local host
        self.host = f"tcp://{tcp_addr}:{port}"

        # The same port as used by the server
        self.port = port

        # open PUB socked for ZMQ
        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.host)

    def run(self):
        # send intial synchronization block
        sync_block = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                              dtype=np.byte)

        for idx, symbol in enumerate(sync_block):
            print(f"sending symbols at {idx:02d}: ", symbol)
            tcp_data = np.array([symbol], dtype=np.byte)
            self.pub_socket.send(tcp_data)

            time.sleep(1)

        while True:
            # add offset 1 in order to encode the next minute
            # and not the current minute
            [day, month, year, hh, mm, ss, weekday, CEST, CET] = \
                self.get_next_time_info(tz="Europe/Berlin", offset=1)

            if ss == "00":
                # triggers at each new minute at 00 seconds
                print(f"new minute: {hh}:{mm}:{ss}")

                # generate some random (useless) weather data
                # NOTE: this will certainly not match the actual DCF77 signal
                weather = np.random.randint(2, size=(14,))

                # encode current time into bit-stream
                bitstream = self.encode_dcf77_bitstream(
                              day=day, month=month, year=year,
                              hh=hh, mm=mm, ss=ss, weekday=weekday,
                              weather=weather,
                              call_bit=False,
                              time_shift=False, time_offset=0,
                              CEST=CEST, CET=CET, leap=False)

                print(f"sending full block: \n {bitstream}\n"
                      " with 1 symbol per second")
                tcp_data = np.array(bitstream, dtype=np.byte)
                self.pub_socket.send(tcp_data)
                time.sleep(1)

            else:
                time.sleep(1)
                print(f"Wait for next minute. Current time: {hh}:{mm}:{ss}")

    def encode_minute(self, mm):
        mm = [int(a) for a in str(mm)]

        # compute bits for minute
        bin_mm_1 = format(mm[1], '04b')
        bin_mm_10 = format(mm[0], '03b')
        listed_val_1 = list(bin_mm_1)
        listed_val_10 = list(bin_mm_10)
        val_1 = [int(x) for x in listed_val_1]
        val_10 = [int(x) for x in listed_val_10]

        # to little endian
        val_1 = val_1[::-1]
        val_10 = val_10[::-1]
        val = val_1 + val_10

        parity = sum(val) % 2
        res = val + [parity]

        return res

    def encode_hour(self, hh):
        hh = [int(a) for a in str(hh)]

        # compute bits for minute
        bin_hh_1 = format(hh[1], '04b')
        bin_hh_10 = format(hh[0], '02b')
        listed_val_1 = list(bin_hh_1)
        listed_val_10 = list(bin_hh_10)
        val_1 = [int(x) for x in listed_val_1]
        val_10 = [int(x) for x in listed_val_10]

        # to little endian
        val_1 = val_1[::-1]
        val_10 = val_10[::-1]
        val = val_1 + val_10

        parity = sum(val) % 2
        res = val + [parity]

        return res

    def encode_cal_day(self, day):
        d = [int(a) for a in str(day)]

        # compute bits for minute
        bin_d_1 = format(d[1], '04b')
        bin_d_10 = format(d[0], '02b')
        listed_val_1 = list(bin_d_1)
        listed_val_10 = list(bin_d_10)
        val_1 = [int(x) for x in listed_val_1]
        val_10 = [int(x) for x in listed_val_10]

        # to little endian
        val_1 = val_1[::-1]
        val_10 = val_10[::-1]
        val = val_1 + val_10

        return val

    def encode_cal_month(self, month):
        m = [int(a) for a in str(month)]

        # compute bits for minute
        bin_m_1 = format(m[1], '04b')
        bin_m_10 = format(m[0], '01b')
        listed_val_1 = list(bin_m_1)
        listed_val_10 = list(bin_m_10)
        val_1 = [int(x) for x in listed_val_1]
        val_10 = [int(x) for x in listed_val_10]

        # to little endian
        val_1 = val_1[::-1]
        val_10 = val_10[::-1]
        val = val_1 + val_10

        return val

    def encode_cal_year(self, year):
        y = [int(a) for a in str(year)]

        # compute bits for minute
        bin_y_1 = format(y[1], '04b')
        bin_y_10 = format(y[0], '04b')
        listed_val_1 = list(bin_y_1)
        listed_val_10 = list(bin_y_10)
        val_1 = [int(x) for x in listed_val_1]
        val_10 = [int(x) for x in listed_val_10]

        # to little endian
        val_1 = val_1[::-1]
        val_10 = val_10[::-1]
        val = val_1 + val_10

        return val

    def encode_weekday(self, weekday):
        binary_string_weekday = format(weekday, '03b')
        listed_val = list(binary_string_weekday)
        val = [int(x) for x in listed_val]

        # to little endian
        val = val[::-1]

        return val

    def parity_date(self, cal_day, cal_weekday, cal_month, cal_year):
        full_date_sum = (sum(cal_day) + sum(cal_weekday)
                         + sum(cal_month) + sum(cal_year))
        parity = full_date_sum % 2
        res = parity
        return res

    def encode_dcf77_bitstream(self,
                               day: int, month: int, year: int,
                               hh: int, mm: int, ss: int, weekday: int,
                               weather,
                               call_bit=False,
                               time_shift=False, time_offset=0,
                               CEST=False, CET=True, leap=False):

        # bit-stream for a full minute
        bitstream = [0 for i in range(60)]

        # [0] start-bit => always zero (indicates start of next minute)
        bitstream[0] = 0

        # [1] .. [14] => zeros (weather-info)
        bitstream[1:15] = weather

        # [15] call bit => (usually) zero
        # ignored
        bitstream[15] = int(call_bit is True)

        # [16] time shift (summer/winter) => (usually) zero
        bitstream[16] = 0

        # [17][18] time offset  => 10 MESZ, 01 MEZ
        bitstream[17] = int(CEST is True)
        bitstream[18] = int(CET is True)

        # [19] leap sec  => (usualy) zero
        bitstream[15] = int(leap is True)

        # [20] => always one
        bitstream[20] = 1

        # [21]...[28] => minute + parity
        bitstream[21:29] = self.encode_minute(mm)

        # [29]...[35] => hour + parity
        bitstream[29:36] = self.encode_hour(hh)

        # [36]...[41] => calender day
        cal_day = self.encode_cal_day(day)
        bitstream[36:42] = cal_day

        # [42]...[44] => weekday (1 monday, 7 sunday)
        cal_weekday = self.encode_weekday(weekday)
        bitstream[42:45] = cal_weekday

        # [45]...[49] => calender month (1, 2, 4, 8, 10)
        cal_month = self.encode_cal_month(month)
        bitstream[45:50] = cal_month

        # [50]...[57] => calender year + parity (1, 2, 4, 8, 10, 20, 40, 80)
        cal_year = self.encode_cal_year(year)
        bitstream[50:58] = cal_year

        # [58] => parity of (cal_day, cal_weekday, cal_month, cal_year)
        bitstream[58] = self.parity_date(cal_day, cal_weekday,
                                         cal_month, cal_year)

        # [59] skip impulse
        # bitstream[59] = 'new minute, 1'
        bitstream[59] = 2

        return bitstream

    def get_next_time_info(self, tz, offset=60):
        """
        NOTE:
        * set offset=60, if you want to provide the next minute to
                         the transmitter
        * set offset=0, if you want to compare the current minute
                         to https://www.dcf77logs.de/live

        :param tz:
        :param offset:
        :return:
        """

        tz_berlin = pytz.timezone(tz)
        now = datetime.now(tz_berlin)

        # NOTE: DCF sends the next minute at hh:mm.00 to come
        # within the current minute (from 0 to 59)
        next = now + timedelta(0, offset)
        CEST = bool(now.dst())
        CET = not bool(CEST)

        # dmy_string = now.strftime("%d/%m/%Y")
        day_string = next.strftime("%d")
        month_string = next.strftime("%m")
        # take only last two digits of year
        year_string = str(int(next.strftime("%Y")) % 100)

        # hhmmss_string = now.strftime("%H:%M:%S")
        hh_string = next.strftime("%H")
        mm_string = next.strftime("%M")
        ss_string = next.strftime("%S")

        # NOTE: weekday number differs between
        # datetime [0,..,6] => [Monday, ..], and
        # DCF77 (ISO 8601) [1,..,7] => [Monday, ..]
        weekday_num = next.weekday() + 1

        # indicate that it is running
        # print("...")

        return [day_string, month_string, year_string, hh_string,
                mm_string, ss_string, weekday_num, CEST, CET]


if __name__ == '__main__':
    my_encoder = DCF77Encoder(port=55552)
    my_encoder.run()
