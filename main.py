from serial.tools import list_ports
from pydobotplus import Dobot, CustomPosition, dobotplus
import time

def read_errors(device: Dobot):
    errors = device.get_alarms()
    if len(errors) != 0:
        print('Errors found:')
        for error in errors:
            print(f'  {error}')

available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[1].device
device = Dobot(port=port)
# device.clear_alarms()
print('CURRENT POSE', device.get_pose())

POSITION_A = CustomPosition(x=283, y=-157, z=-49, r=-74)
POSITION_A_HIGH = CustomPosition(x=204.751953125, y=-183.9032440185547, z=111.17557525634766, r=-74)
POSITION_B_HIGH = CustomPosition(x=-17.023897171020508, y=-280.9414367675781, z=111.17557525634766, r=-170)
POSITION_B = CustomPosition(x=-29.64458656311035, y=-303.1400146484375, z=0.9083023071289062, r=-170)
POSITION_HOME = CustomPosition(x=269, y=9, z=123, r=0)

device.move_to(position=POSITION_HOME)

device.move_to(position=POSITION_A)
device.grip(True)
time.sleep(0.5)
device.move_to(position=POSITION_A_HIGH)
device.move_to(position=POSITION_B_HIGH)
device.move_to(position=POSITION_B)
device.grip(False)
time.sleep(0.5)
device.move_to(position=POSITION_B_HIGH)
device.move_to(position=POSITION_HOME)
device.close()