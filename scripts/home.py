import argparse
from serial.tools import list_ports
from pydobotplus import Dobot
from dobot_config import PORT_MAP, HOME_POSITIONS


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Home a Dobot")
    parser.add_argument(
        "--robot",
        choices=["loader", "unloader"],
        required=True,
        help="Which robot to home (loader or unloader)",
    )
    parser.add_argument("--port", help="Manually specify serial port")

    args = parser.parse_args()

    # Get available ports
    available_ports = list_ports.comports()
    print(f"Available ports: {[x.device for x in available_ports]}")

    # Determine which port to use
    if args.port:
        port = args.port
    else:
        # Use the PORT_MAP to determine which port to use
        if args.robot in PORT_MAP:
            port = PORT_MAP[args.robot]
        else:
            print(f"Error: Unknown robot type: {args.robot}")
            return

    print(f"Connecting to {args.robot} on port {port}")
    device = Dobot(port=port)

    # Home position settings from centralized configuration
    home_pos = HOME_POSITIONS.get(args.robot)
    if home_pos:
        device.set_home(**home_pos)
    else:
        # Fallback to default if not in config
        device.set_home(x=269.068, y=9.949, z=123.561, r=0)

    print(f"Moving {args.robot} to home position...")
    device.home()
    print("Homing complete")

    device.close()
    print(f"Connection to {args.robot} closed")


if __name__ == "__main__":
    main()
