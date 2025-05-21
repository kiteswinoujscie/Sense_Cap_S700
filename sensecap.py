import weewx.drivers
from weewx.drivers import AbstractDevice
import minimalmodbus
import time
import syslog
import weewx

DRIVER_NAME = "SenseCAP"
DRIVER_VERSION = "1.0"

def loader(config_dict, engine):
    return SenseCAPDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return SenseCAPConfEditor()

class SenseCAPDriver(AbstractDevice):
    def __init__(self, **stn_dict):
        port = stn_dict.get('port', '/dev/ttyUSB0')
        self.poll_interval = int(stn_dict.get('poll_interval', 60))

        self.instrument = minimalmodbus.Instrument(port, 1)  # Modbus address = 1
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 1
        self.instrument.mode = minimalmodbus.MODE_RTU

    def genLoopPackets(self):
        while True:
            try:
                data = self._read_data()
                packet = {
                    'dateTime': int(time.time() + 0.5),
                    'usUnits': weewx.METRIC,
                    'outTemp': data['temperature'],
                    'outHumidity': data['humidity'],
                    'pressure': data['pressure'],         # w hPa
                    'windSpeed': data['wind_speed'],      # w węzłach
                    'windDir': data['wind_dir'],          # w stopniach
                    'rain': data['rain'],                 # mm/h
                }
                yield packet
            except Exception as e:
                syslog.syslog(syslog.LOG_ERR, f"SenseCAP: Błąd odczytu danych: {e}")
            time.sleep(self.poll_interval)

    def _read_register32(self, register_address):
        try:
            raw = self.instrument.read_registers(register_address, 2)
            value = (raw[0] << 16) + raw[1]
            return value
        except Exception as e:
            raise Exception(f"Błąd odczytu rejestru 0x{register_address:04X}: {e}")

    def _read_data(self):
        try:
            t = self._read_register32(0x0000) / 1000.0        # temperatura (°C)
            h = self._read_register32(0x0002) / 1000.0        # wilgotność (%)
            p = self._read_register32(0x0004) / 1000000.0      # ciśnienie (hPa)
            ws = self._read_register32(0x0012) / 100.0        # prędkość wiatru (m/s)
            wd = self._read_register32(0x000C) / 1000.0       # kierunek wiatru (°)
            rain = self._read_register32(0x0018) / 100.0      # opad chwilowy (mm/h)

            wind_speed_knots = round(ws * 1.94384, 2)

            return {
                'temperature': round(t, 2),
                'humidity': round(h, 2),
                'pressure': round(p * 10, 2),  # weewx oczekuje w hPa, ale może być konwersja na inHg, jeśli używasz IMPERIAL
                'wind_speed': wind_speed_knots,
                'wind_dir': round(wd, 2),
                'rain': round(rain, 2)
            }
        except Exception as e:
            raise e

    @property
    def hardware_name(self):
        return "SenseCAP"

class SenseCAPConfEditor:
    @staticmethod
    def get_config():
        return {
            'SenseCAP': {
                'driver': 'user.sensecap',
                'port': '/dev/ttyUSB0',
                'poll_interval': '30',
            }
        }
