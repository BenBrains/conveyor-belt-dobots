#!/usr/bin/env python3
# filepath: /home/baljeet/conveyor-belt-dobots/main.py
from serial.tools import list_ports
from pydobotplus import Dobot, CustomPosition, dobotplus
import time
import sys
import argparse
from typing import Optional, List, Dict
import sys
import os

# Add the scripts directory to the path so we can import the config
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
from dobot_config import PORT_MAP


class RobotPositions:
    """Store and manage robot position definitions for multiple robots."""

    def __init__(self, robot_id: str = "loader"):
        """Initialize positions for a specific robot.

        Args:
            robot_id: Identifier for the robot ("loader" or "unloader")
        """
        self.robot_id = robot_id

        # Positions for the first robot (conveyor loader robot)
        if robot_id == "loader":
            # Pick location
            self.POSITION_A = CustomPosition(
                x=106.02387237548828, y=-187.68869018554688, z=44.56678009033203, r=-75
            )
            self.POSITION_A_HIGH = CustomPosition(
                x=106.02387237548828, y=-187.68869018554688, z=111, r=-75
            )

            # Place location
            self.POSITION_B = CustomPosition(
                x=-29.64458656311035, y=-303.1400146484375, z=0.9083023071289062, r=-170
            )
            self.POSITION_B_HIGH = CustomPosition(
                x=-17.023897171020508, y=-280.9414367675781, z=111, r=-170
            )

            # Home position (using position A high as default)
            self.POSITION_HOME = self.POSITION_A_HIGH

        # Positions for the second robot (conveyor unloader robot)
        elif robot_id == "unloader":
            # Pick location
            self.POSITION_A = CustomPosition(
                x=-31.562040328979492, y=224.74261474609375, z=-8.261711120605469, r=240
            )
            self.POSITION_A_HIGH = CustomPosition(
                x=-25.590173721313477, y=199.59945678710938, z=47.82006072998047, r=240
            )

            # Place location
            self.POSITION_B = CustomPosition(
                x=99.32231903076172, y=192.50628662109375, z=43.28069305419922, r=240
            )
            self.POSITION_B_HIGH = CustomPosition(
                x=99.32231903076172, y=192.50628662109375, z=111, r=240
            )

            # Home position
            self.POSITION_HOME = self.POSITION_A_HIGH
        else:
            raise ValueError(
                f"Unknown robot_id: {robot_id}. Use 'loader' or 'unloader'."
            )


class DobotController:
    """Main controller for Dobot operations."""

    def __init__(
        self,
        robot_id: str = "loader",
        port: Optional[str] = None,
        positions: Optional[RobotPositions] = None,
    ):
        """Initialize the Dobot controller with specified port and positions.

        Args:
            robot_id: Identifier for the robot ("loader" or "unloader")
            port: Optional specific port to use (overrides robot_id port mapping)
            positions: Optional specific positions to use (otherwise created based on robot_id)
        """
        self.robot_id = robot_id
        self.port = port or self._get_port_for_robot(robot_id)
        self.positions = positions or RobotPositions(robot_id)
        self.device = None

    def _get_port_for_robot(self, robot_id: str) -> str:
        """Get the appropriate port for the specified robot."""
        if robot_id in PORT_MAP:
            return PORT_MAP[robot_id]
        else:
            return self._auto_detect_port()

    def _auto_detect_port(self) -> str:
        """Auto-detect available serial ports for the Dobot."""
        available_ports = list_ports.comports()
        if not available_ports:
            raise ConnectionError(
                "No serial ports available. Please check connections."
            )

        print(f"[INFO] Available ports: {[x.device for x in available_ports]}")

        # Look for USB ports
        usb_ports = [p.device for p in available_ports if "USB" in p.device]
        if usb_ports:
            return usb_ports[0]  # Return the first USB port

        # Fallback to the first available port
        return available_ports[0].device

    def connect(self) -> bool:
        """Connect to the Dobot device."""
        try:
            self.device = Dobot(port=self.port)
            print(f"[INFO] Connected to {self.robot_id} at {self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect {self.robot_id} at {self.port}: {e}")
            return False

    def check_errors(self) -> List[str]:
        """Check for any alarms/errors on the Dobot device."""
        if not self.device:
            return [f"[ERROR] {self.robot_id} not connected"]

        errors = self.device.get_alarms()
        if errors:
            print(f"[INFO] Errors found on {self.robot_id}:")
            for error in errors:
                print(f"  {error}")
        return errors

    def clear_errors(self) -> None:
        """Clear any alarms/errors on the Dobot device."""
        if self.device:
            self.device.clear_alarms()

    def move_to(self, position: CustomPosition) -> None:
        """Move the Dobot to a specific position."""
        if self.device:
            try:
                self.device.move_to(position=position)
            except Exception as e:
                print(f"[ERROR] Movement error on {self.robot_id}: {e}")

    def grip(self, close: bool, delay: float = 0.5) -> None:
        """Operate the gripper."""
        if self.device:
            try:
                self.device.grip(close)
                time.sleep(delay)  # Allow time for the gripper to complete action
            except Exception as e:
                print(f"[ERROR] Gripper error on {self.robot_id}: {e}")

    def pick_and_place(
        self,
        pick_pos: CustomPosition,
        pick_approach: CustomPosition,
        place_pos: CustomPosition,
        place_approach: CustomPosition,
        return_home: bool = True,
    ) -> None:
        """Execute a complete pick and place operation."""
        # Approach pick position
        self.move_to(pick_approach)

        # Pick
        self.move_to(pick_pos)
        self.grip(True)

        # Retreat from pick position
        self.move_to(pick_approach)

        # Approach place position
        self.move_to(place_approach)

        # Place
        self.move_to(place_pos)
        self.grip(False)

        # Retreat from place position
        self.move_to(place_approach)

        # Return to home if requested
        if return_home:
            self.move_to(self.positions.POSITION_HOME)

    def close(self) -> None:
        """Close the connection to the Dobot device."""
        if self.device:
            try:
                self.device.close()
                print(f"[INFO] Connection to {self.robot_id} closed")
            except Exception as e:
                print(f"[ERROR] Error closing connection to {self.robot_id}: {e}")
            self.device = None


def run_dobot_operation(robot_id: str, port: Optional[str] = None) -> None:
    """Run operations for a specific Dobot.

    Args:
        robot_id: Identifier for the robot ("loader" or "unloader")
        port: Optional specific port to use
    """
    # Initialize controller
    controller = DobotController(robot_id=robot_id, port=port)

    # Connect to Dobot
    if not controller.connect():
        print(f"[ERROR] Failed to connect to {robot_id}. Exiting.")
        return

    try:
        # Check and clear errors if any
        errors = controller.check_errors()
        if errors:
            print(f"[INFO] Errors on {robot_id}: {errors}")
            controller.clear_errors()

        # Move to home position first
        controller.move_to(controller.positions.POSITION_HOME)

        # Execute pick and place operation
        controller.pick_and_place(
            pick_pos=controller.positions.POSITION_A,
            pick_approach=controller.positions.POSITION_A_HIGH,
            place_pos=controller.positions.POSITION_B,
            place_approach=controller.positions.POSITION_B_HIGH,
        )

    except KeyboardInterrupt:
        print(f"\n[ERROR] Operation interrupted by user for {robot_id}")
    except Exception as e:
        print(f"[ERROR] Error during operation for {robot_id}: {e}")
    finally:
        # Always ensure we close the connection properly
        controller.close()


def run_dual_robot_sequence():
    """Run a coordinated sequence using both robots."""
    # Initialize controllers for both robots
    loader = DobotController(robot_id="loader")
    unloader = DobotController(robot_id="unloader")

    # Connect to both robots
    if not loader.connect():
        print("[ERROR] Failed to connect to loader. Exiting.")
        return

    if not unloader.connect():
        print("[ERROR] Failed to connect to unloader. Exiting.")
        loader.close()
        return

    try:
        # Check and clear errors for both robots
        for robot in [loader, unloader]:
            errors = robot.check_errors()
            if errors:
                print(f"[INFO] Errors on {robot.robot_id}: {errors}")
                robot.clear_errors()

            # Move both to home positions
            robot.move_to(robot.positions.POSITION_HOME)

        # Robot 1 picks and places onto conveyor
        loader.pick_and_place(
            pick_pos=loader.positions.POSITION_A,
            pick_approach=loader.positions.POSITION_A_HIGH,
            place_pos=loader.positions.POSITION_B,
            place_approach=loader.positions.POSITION_B_HIGH,
            return_home=True,
        )

        # Small delay to simulate conveyor movement
        time.sleep(2)

        # Robot 2 picks from conveyor and places onto second belt
        unloader.pick_and_place(
            pick_pos=unloader.positions.POSITION_A,
            pick_approach=unloader.positions.POSITION_A_HIGH,
            place_pos=unloader.positions.POSITION_B,
            place_approach=unloader.positions.POSITION_B_HIGH,
            return_home=True,
        )

    except KeyboardInterrupt:
        print("\n[ERROR] Dual robot operation interrupted by user")
    except Exception as e:
        print(f"[ERROR] Error during dual robot operation: {e}")
    finally:
        # Always ensure we close the connections properly
        loader.close()
        unloader.close()


def main():
    """Main execution function with command-line argument support."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Dobot Conveyor Belt Controller")
    parser.add_argument(
        "--robot",
        choices=["loader", "unloader", "both"],
        default="both",
        help="Which robot to operate (loader, unloader, or both)",
    )
    parser.add_argument("--port1", help="Serial port for loader (overrides default)")
    parser.add_argument("--port2", help="Serial port for unloader (overrides default)")

    # Parse arguments
    args = parser.parse_args()

    # Run operations based on the robot selection
    if args.robot == "loader":
        run_dobot_operation("loader", args.port1)
    elif args.robot == "unloader":
        run_dobot_operation("unloader", args.port2)
    else:  # args.robot == "both"
        # Override default port mapping if provided
        if args.port1:
            DobotController.PORT_MAP["loader"] = args.port1
        if args.port2:
            DobotController.PORT_MAP["unloader"] = args.port2

        run_dual_robot_sequence()


if __name__ == "__main__":
    main()
