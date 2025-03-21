"""Example to find all Free-Wilis connected over USB."""

import result

from freewili import FreeWili

# Find the first device and raise an exception otherwise
try:
    device = FreeWili.find_first().expect("Failed to find a FreeWili")
except result.UnwrapError as ex:
    print(ex)

# Find all and display information about it.
devices = FreeWili.find_all()
print(f"Found {len(devices)} FreeWili(s)")
for i, free_wili in enumerate(devices, start=1):
    print(f"{i}. {free_wili}")
    print(f"\t{free_wili.main}")
    print(f"\t{free_wili.display}")
    print(f"\t{free_wili.ftdi}")
