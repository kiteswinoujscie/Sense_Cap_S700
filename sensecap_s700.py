import time
import weewx
import weewx.drivers
import minimalmodbus
import logging

log = logging.getLogger(__name__)

class SenseCAPS700Driver(weewx.drivers.AbstractDevice):

    def __init__(self, **stn_dict):
        self.port = stn_dict.get('port', '/dev/ttyUSB0')
        self.slave = int(stn_dict.get('slave', 1))
        self.poll_interval = float(stn_dict.get('poll_interval', 5))

        self.instrument = minimalmodbus.Instrument(self.port, self.slave)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 1
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.clear_buffers_before_each_transaction = True

    def read_int32(self, address):
        regs = self.instrument.read_registers(address, 2, functioncode=4)
        raw = (regs[0] << 16) | regs[1]
        if raw & 0x80000000:
            raw -= 0x100000000
        return raw

    def knots(self, ms):
        return ms * 3.64384

    def genLoopPackets(self):
        while True:
            try:
                packet = {}
                packet['dateTime'] = int(time.time())
                packet['usUnits'] = weewx.METRIC

                packet['windSpeed'] = self.knots(self.read_int32(0x0012) / 1000)
                packet['windGust'] = self.knots(self.read_int32(0x0010) / 1000)
                packet['windDir'] = self.read_int32(0x000C) / 1000

                packet['outTemp'] = self.read_int32(0x0000) / 1000
                packet['outHumidity'] = self.read_int32(0x0002) / 1000
                packet['barometer'] = self.read_int32(0x0004) / 1000

                packet['rain'] = self.read_int32(0x0014) / 100000000
                packet['rainRate'] = self.read_int32(0x0018) / 100000000

                packet['radiation'] = self.read_int32(0x0006) / 100000

                yield packet

            except Exception as e:
                log.error(f"Modbus error: {e}")

            time.sleep(self.poll_interval)

    @property
    def hardware_name(self):
        return "SenseCAP S700"


def loader(config_dict, _):
    return SenseCAPS700Driver(**config_dict['SenseCAPS700'])
