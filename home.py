from serial.tools import list_ports
from pydobotplus import Dobot, CustomPosition

available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[1].device
device = Dobot(port=port)

device.set_home(x=269.068, y=9.949, z=123.561, r=0)
device.home()

device.close()