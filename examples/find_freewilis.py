"""Example to find all Free-Wilis connected over USB."""

from freewili import FreeWili

devices = FreeWili.find_all()
print(f"Found {len(devices)} FreeWili(s)")
for i, free_wili in enumerate(devices, start=1):
    print(f"{i}. {free_wili}")
    print(f"\t{free_wili.main}")
    print(f"\t{free_wili.display}")
    print(f"\t{free_wili.ftdi}")
