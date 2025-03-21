"""Set Board RGB on a Free-Wili."""

import time

from result import Err, Ok

from freewili import FreeWili
from freewili.framing import ResponseFrame


def check_resp(device: FreeWili, resp: ResponseFrame) -> None:
    """Check the response and exit on error."""
    if not resp.is_ok():
        print(f"Response failed: {resp.response}")
        device.close()
        exit(1)


# find a FreeWili device
match FreeWili.find_first():
    case Ok(d):
        device = d
        device.stay_open = True
        print(f"Using {device}")
    case Err(msg):
        print(msg)
        exit(1)

try:
    # Turn the LEDs on
    for led_num in range(7):
        resp = device.set_board_leds(led_num, 10, 10, led_num * 2).expect("Failed to set LED")
        check_resp(device, resp)
    # Wait so we can see them
    time.sleep(3)
    # Turn the LEDS off
    for led_num in reversed(range(7)):
        resp = device.set_board_leds(led_num, 0, 0, 0).expect("Failed to set LED")
        check_resp(device, resp)

finally:
    device.close()
