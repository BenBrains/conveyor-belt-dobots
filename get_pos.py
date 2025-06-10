from serial.tools import list_ports
from pydobotplus import Dobot, CustomPosition

available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[1].device
device = Dobot(port=port)
print('CURRENT POSE', device.get_pose())

device.close()