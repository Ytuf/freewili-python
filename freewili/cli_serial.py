"""Command line serial interface for the FreeWili library.

This module provides a command line interface to find and control FreeWili boards.
"""

import argparse
import importlib.metadata
import pathlib

from result import Err, Ok

from freewili import FreeWili
from freewili.cli import exit_with_error, get_device
from freewili.fw import GPIO_MAP
from freewili.serial_util import FreeWiliProcessorType, IOMenuCommand


def main() -> None:
    """A command line interface to list and control FreeWili boards.

    Parameters:
    ----------
        None

    Returns:
    -------
        None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="List all FreeWili connected to the computer.",
    )
    parser.add_argument(
        "-i",
        "--index",
        type=int,
        default=1,
        help="Select a specific FreeWili by index. The first FreeWili is 1.",
    )
    parser.add_argument(
        "-di",
        "--display_index",
        type=int,
        default=None,
        help="Select a specific FreeWili display processor by index. The first FreeWili is 1.",
    )
    parser.add_argument(
        "-mi",
        "--main_index",
        type=int,
        default=None,
        help="Select a specific FreeWili main processor by index. The first FreeWili is 1.",
    )
    parser.add_argument(
        "-s",
        "--send_file",
        nargs=1,
        help="send a file to the FreeWili. Argument should be in the form of: <source_file>",
    )
    parser.add_argument(
        "-fn",
        "--file_name",
        nargs=1,
        help="Set the name of the file in the FreeWili. Argument should be in the form of: <file_name>",
    )
    # parser.add_argument(
    #     "-u",
    #     "--get_file",
    #     nargs=2,
    #     help="Get a file from the FreeWili. Argument should be in the form of: <source_file> <target_name>",
    # )
    parser.add_argument(
        "-w",
        "--run_script",
        nargs="?",
        const=False,
        help="Run a script on the FreeWili. If no argument is provided, -fn will be used.",
    )
    parser.add_argument(
        "-io",
        "--io",
        nargs="*",
        help=(
            "Set IO. Argument should be in the form of: <io_pin> <high/low/toggle/pwm> [pwm_freq] [pwm_duty].\n"
            "No arguments gets all IO values."
        ),
    )
    parser.add_argument(
        "-led",
        "--led",
        nargs=4,
        help="Set Board LEDs. Argument should be in the form of: <LED #> <red 0-255> <green 0-255> <blue 0-255>",
    )
    parser.add_argument(
        "-gi",
        "--gui_image",
        nargs=1,
        help="Show GUI Image. Argument should be in the form of: <image path>",
    )
    parser.add_argument(
        "-gt",
        "--gui_text",
        nargs=1,
        help="Show GUI Text. Argument should be in the form of: <text>",
    )
    parser.add_argument(
        "-rb",
        "--read_buttons",
        action="store_true",
        default=False,
        help="Read buttons.",
    )
    parser.add_argument(
        "-rd",
        "--reset_display",
        action="store_true",
        default=False,
        help="Reset the display back to the main menu.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=importlib.metadata.version("freewili")),
    )
    args = parser.parse_args()
    device_index: int = args.index - 1
    processor_type = None
    if args.main_index is not None:
        processor_type = FreeWiliProcessorType.Main
    elif args.display_index is not None:
        processor_type = FreeWiliProcessorType.Display
    devices = FreeWili.find_all()
    if args.list:
        print(f"Found {len(devices)} FreeWili(s)")
        for i, free_wili in enumerate(devices, start=1):
            print(f"{i}. {free_wili}")
            print(f"\t{free_wili.main}")
            print(f"\t{free_wili.display}")
            print(f"\t{free_wili.ftdi}")
    if args.send_file:
        match get_device(device_index, devices):
            case Ok(device):
                file_name = None
                if args.file_name:
                    file_name = args.file_name[0]
                print(device.send_file(args.send_file[0], file_name, processor_type).unwrap())
            case Err(msg):
                exit_with_error(msg)
    # if args.get_file:
    #     match get_device(device_index, devices):
    #         case Ok(device):
    #             data = device.get_file(args.get_file[0]).unwrap()
    #             with open(args.get_file[1], "w+b") as f:
    #                 f.write(data)
    #         case Err(msg):
    #             exit_with_error(msg)
    if args.run_script is not None:
        match get_device(device_index, devices):
            case Ok(device):
                if args.run_script:
                    script_name = args.run_script
                elif args.file_name:
                    script_name = args.file_name[0]
                elif args.send_file:
                    script_name = pathlib.Path(args.send_file[0]).name
                else:
                    raise ValueError("No script or file name provided")
                print(device.run_script(script_name).unwrap())
            case Err(msg):
                exit_with_error(msg)
    if args.io is not None:
        io_args_length = len(args.io)
        if io_args_length == 0:
            match get_device(device_index, devices):
                case Ok(device):
                    print("Getting IO pin values...")
                    match device.get_io():
                        case Ok(values):
                            for io_num, io_name in GPIO_MAP.items():
                                print(f"{io_name}: {values[io_num]}")
                        case Err(msg):
                            exit_with_error(msg)
                case Err(msg):
                    exit_with_error(msg)
        else:
            io_pin: int = int(args.io[0])
            menu_cmd: IOMenuCommand = IOMenuCommand.from_string(args.io[1].lower())
            pwm_freq_hz = None
            pwm_duty_cycle = None
            if menu_cmd is IOMenuCommand.Pwm:
                io_args_length = len(args.io)
                if io_args_length < 4:
                    exit_with_error(f"Expected 4 parameters to -io, got {io_args_length}")
                pwm_freq_hz = int(args.io[2])
                pwm_duty_cycle = int(args.io[3])
            match get_device(device_index, devices):
                case Ok(device):
                    print(f"Setting IO pin {io_pin} {menu_cmd.name} ", end="")
                    if io_args_length >= 4:
                        print(f"PWM Frequency: {pwm_freq_hz}Hz {pwm_duty_cycle}%", end="")
                    print()
                    resp = device.set_io(io_pin, menu_cmd, pwm_freq_hz, pwm_duty_cycle).unwrap_or(
                        "Failed to configure IO pin"
                    )
                    if not resp.is_ok():
                        exit_with_error(f"Failed to configure IO pin: {resp.response}")
                    print(f"Successfully configured pin {io_pin} {menu_cmd.name}")
                case Err(msg):
                    exit_with_error(msg)
    if args.led:
        led_num = args.led[0]
        red = args.led[1]
        green = args.led[2]
        blue = args.led[3]
        match get_device(device_index, devices):
            case Ok(device):
                print(f"Setting LED {led_num} to RGB: {red}, {green}, {blue}...")
                match device.set_board_leds(led_num, red, green, blue):
                    case Ok(resp):
                        if not resp.is_ok():
                            exit_with_error(f"Failed to set LED {resp.response}")
                        else:
                            print(f"Successfully set LED {led_num}")
                    case Err(msg):
                        exit_with_error(msg)
            case Err(msg):
                exit_with_error(msg)
    if args.gui_image:
        value = args.gui_image[0]
        match get_device(device_index, devices):
            case Ok(device):
                print(f"Showing Image {value}...")
                match device.show_gui_image(value):
                    case Ok(resp):
                        if not resp.is_ok():
                            exit_with_error(f"Failed to show Image {resp.response}")
                        else:
                            print(f"Successfully showing {value}")
                    case Err(msg):
                        exit_with_error(msg)
            case Err(msg):
                exit_with_error(msg)
    if args.gui_text:
        value = args.gui_text[0]
        match get_device(device_index, devices):
            case Ok(device):
                print(f"Showing text {value}...")
                match device.show_text_display(value):
                    case Ok(resp):
                        if not resp.is_ok():
                            exit_with_error(f"Failed to show text {resp.response}")
                        else:
                            print(f"Successfully showing {value}")
                    case Err(msg):
                        exit_with_error(msg)
            case Err(msg):
                exit_with_error(msg)
    if args.read_buttons:
        match get_device(device_index, devices):
            case Ok(device):
                print("Getting button values...")
                match device.read_all_buttons():
                    case Ok(resp):
                        if not resp.is_ok():
                            exit_with_error(f"Failed to show text {resp.response}")
                        else:
                            print(resp.response)
                    case Err(msg):
                        exit_with_error(msg)
            case Err(msg):
                exit_with_error(msg)
    if args.reset_display:
        match get_device(device_index, devices):
            case Ok(device):
                print("Resetting display...")
                match device.reset_display():
                    case Ok(resp):
                        if not resp.is_ok():
                            exit_with_error(f"Failed to reset display {resp.response}")
                        else:
                            print(resp.response)
                    case Err(msg):
                        exit_with_error(msg)
            case Err(msg):
                exit_with_error(msg)


if __name__ == "__main__":
    main()
