"""Command line interface for converting images.

This module provides a command line interface to find and control FreeWili boards.
"""

import argparse
import importlib.metadata

from result import Err, Ok

from freewili import image
from freewili.cli import exit_with_error


def main() -> None:
    """A command line interface to convert a jpg or png image to a fwi file.

    Parameters:
    ----------
        None

    Returns:
    -------
        None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to a JPG or PNG image to be converted",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output filename for the fwi file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=importlib.metadata.version("freewili")),
    )
    args = parser.parse_args()
    match image.convert(args.input, args.output):
        case Ok(msg):
            print(msg)
        case Err(msg):
            exit_with_error(msg)


if __name__ == "__main__":
    main()
