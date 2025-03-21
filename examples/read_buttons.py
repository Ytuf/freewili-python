"""Read buttons on a Free-Wili."""

from result import Err, Ok

from freewili import FreeWili
from freewili.framing import ResponseFrame


def check_resp(device: FreeWili, resp: ResponseFrame) -> None:
    """Check the response and exit on error."""
    if not resp.is_ok():
        print(f"Response failed: {resp.response}")
        device.close()
        exit(1)


BUTTON_COLOR = ["White", "Yellow", "Green", "Blue", "Red"]

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
    # Read the buttons and print on change
    print("Reading buttons...")
    last_read = bytes([0, 0, 0, 0, 0])
    while True:
        try:
            resp = device.read_all_buttons().expect("Failed to read buttons")
            check_resp(device, resp)
            buttons = resp.response_as_bytes().expect("Failed to convert response")
            for i, button in enumerate(buttons):
                if last_read[i] != button:
                    state = "Pressed \N{WHITE HEAVY CHECK MARK}"
                    if button == 0:
                        state = "Released \N{CROSS MARK}"
                    print(f"{BUTTON_COLOR[i]} {state}")
            last_read = buttons
        except KeyboardInterrupt:
            break
finally:
    device.close()
