"""Toggle IO on a Free-Wili."""

from freewili import FreeWili

# Find connected Free-Wilis
devices = FreeWili.find_all()
if not devices:
    print("No Free-Wili devices found!")
    exit(1)

# Pick the first Free-Wili
device = devices[0]

# Toggle IO pin 0
device.set_io(0, True).expect("Failed to set IO high")
device.set_io(0, False).expect("Failed to set IO low")
