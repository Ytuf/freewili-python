"""Command line interface utilities for the FreeWili library.

This module provides a command line interface to find and control FreeWili boards.
"""

import sys

from result import Err, Ok, Result

from freewili.fw import FreeWili


def exit_with_error(msg: str, exit_code: int = 1) -> None:
    """A function that prints an error message to the stderr and exits the program with a specified exit code.

    Parameters:
    ----------
        msg: str
            The error message to be printed.
        exit_code: int, optional
            The exit code to be used when exiting the program, defaults to 1.

    Returns:
    -------
        None
    """
    print(msg, file=sys.stderr)
    sys.exit(exit_code)


def get_device(
    index: int,
    devices: tuple[FreeWili, ...],
) -> Result[FreeWili, str]:
    """Get a FreeWili by index.

    Parameters:
    ----------
        index: int
            The index to be checked.

        devices: tuple[FreeWili]
            container of FreeWili to reference

    Returns:
    -------
        Result[FreeWili, str]:
            The FreeWili if the index is valid, otherwise an error message.
    """
    if index >= len(devices):
        return Err(f"Index {index} is out of range. There are only {len(devices)} devices.")
    return Ok(devices[index])
