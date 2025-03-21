"""Toggle IO on a Free-Wili."""

from result import Err, Ok

from freewili import FreeWili
from freewili.framing import ResponseFrame
from freewili.serial_util import IOMenuCommand


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
    # Set IO 25 high
    resp = device.set_io(25, IOMenuCommand.High).expect("Failed to set IO high")
    check_resp(device, resp)

    # Set IO 25 Low
    resp = device.set_io(25, IOMenuCommand.Low).expect("Failed to set IO low")
    check_resp(device, resp)

    # Toggle IO 25 Low
    resp = device.set_io(25, IOMenuCommand.Toggle).expect("Failed to toggle IO")
    check_resp(device, resp)

    # PWM IO 25
    resp = device.set_io(25, IOMenuCommand.Pwm, 10, 50).expect("Failed to toggle IO")
    check_resp(device, resp)
finally:
    device.close()
