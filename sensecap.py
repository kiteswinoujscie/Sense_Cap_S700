
#!/usr/bin/env python

import minimalmodbus
import time
import syslog
import weewx
import weewx.drivers

DRIVER_NAME = "SenseCAP"
DRIVER_VERSION = "0.3"

def logmsg(dst, msg):
    syslog.syslog(dst, f"{DRIVER_NAME}: {msg}")

def loginf(msg): logmsg(syslog.LOG_INFO, msg)
def logdbg(msg): logmsg(syslog.LOG_DEBUG, msg)

def loader(config_dict, _): return SenseCAPDriver(**config_dict[DRIVER_NAME])
def confeditor_loader(): return SenseCAPConfEditor()

class SenseCAPConfEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return f"""
[{DRIVER_NAME}]
    model = SenseCAP S700
    port = /dev/ttyUSB0
    poll_interval = 10
    address = 1
    driver = user.sensecap
"""

class SenseCAPDriver(weewx.drivers.AbstractDevice):
    def __init__(self, **stn_dict):
        self.model = stn_dict.get("model", "SenseCAP S700")
        self.port = stn_dict.get("port", "/dev/ttyUSB0")
        self.poll_interval = int(stn_dict.get("poll_interval", 10))
        self.address = int(stn_dict.get("address", 1))
        self.instrument = minimalmodbus.Instrument(self.port, self.address)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 1
        self.last_rain_total = None
        loginf(f"Initialized {self.model} on {self.port}")

    @property
    def hardware_name(self):
        return self.model

    def closePort(self):
        self.instrument.serial.close()

    def genLoopPackets(self):
        while True:
            try:
                data = self.read_sensor_data()
                packet = {
                    'dateTime': int(time.time()),
                    'usUnits': weewx.METRIC,
                    **data
                }
                yield packet
                time.sleep(self.poll_interval)
            except Exception as e:
                logmsg(syslog.LOG_ERR, f"Error: {e}")
                time.sleep(self.poll_interval)

    def read_sensor_data(self):
        r = self.instrument.read_registers
        def read_int32(addr):
            h, l = r(addr, 2)
            return (h << 16) + l

        curr_rain_total = read_int32(0x0014) / 1000.0  # mm
        rain_delta = 0.0
        if self.last_rain_total is not None:
            rain_delta = max(0.0, curr_rain_total - self.last_rain_total)
        self.last_rain_total = curr_rain_total

        data = {
            'outTemp': read_int32(0x0000) / 1000.0,         # °C
            'outHumidity': read_int32(0x0002) / 1000.0,     # %RH
            'pressure': read_int32(0x0004) / 100000.0,        # hPa
            'radiation': read_int32(0x0006) / 1000.0,       # lux
            'windDir': read_int32(0x000C) / 1000.0,         # degrees
            'windSpeed': read_int32(0x0012) / 1000.0,       # m/s
            'windGust': read_int32(0x0010) / 1000.0,        # m/s
            'rainRate': read_int32(0x0018) / 1000.0,        # mm/min
            'rain': rain_delta                             # mm od ostatniego odczytu
        }
        return data
