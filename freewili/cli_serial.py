"""Command line serial interface for the FreeWili library.

This module provides a command line interface to find and control FreeWili boards.
"""

import argparse
import importlib.metadata
import pathlib

from result import Err, Ok

from freewili import serial
from freewili.cli import exit_with_error, get_device
from freewili.serial import FreeWiliProcessorType


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
    parser.add_argument(
        "-u",
        "--get_file",
        nargs=2,
        help="Get a file from the FreeWili. Argument should be in the form of: <source_file> <target_name>",
    )
    parser.add_argument(
        "-w",
        "--run_script",
        nargs="?",
        const=False,
        help="Run a script on the FreeWili. If no argument is provided, -fn will be used.",
    )
    parser.add_argument(
        "-io",
        "--set_io",
        nargs=2,
        help="Toggle IO pin to high. Argument should be in the form of: <io_pin> <high/low>",
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

    if args.list:
        devices = serial.find_all(processor_type)
        print(f"Found {len(devices)} FreeWili(s)")
        for i, free_wili in enumerate(devices, start=1):
            print(f"\t{i}. {free_wili}")
    if args.send_file:
        match get_device(device_index, processor_type):
            case Ok(device):
                if args.file_name:
                    file_name = args.file_name[0]
                else:
                    file_name = "/scripts/" + pathlib.Path(args.send_file[0]).name
                print(device.send_file(args.send_file[0], file_name).unwrap())
            case Err(msg):
                exit_with_error(msg)
    if args.get_file:
        match get_device(device_index, processor_type):
            case Ok(device):
                data = device.get_file(args.get_file[0]).unwrap()
                with open(args.get_file[1], "w+b") as f:
                    f.write(data)
            case Err(msg):
                exit_with_error(msg)
    if args.run_script is not None:
        match get_device(device_index, processor_type):
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
    if args.set_io:
        io_pin: int = int(args.set_io[0])
        is_high: bool = args.set_io[1].upper() == "HIGH"
        match get_device(device_index, processor_type):
            case Ok(device):
                print("Setting IO pin", io_pin, "to", "high" if is_high else "low")
                print(device.set_io(io_pin, is_high).unwrap_or("Failed to set IO pin"))
            case Err(msg):
                exit_with_error(msg)


if __name__ == "__main__":
    main()
