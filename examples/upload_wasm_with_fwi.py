"""Upload a wasm file to a Free-Wili."""

import pathlib

from freewili import FreeWili

# The fwi file to upload
my_fwi_file = pathlib.Path(r"~/path/to/MyFile.fwi")
# The wasm file to upload
my_wasm_file = pathlib.Path(r"~/path/to/MyFile.wasm")

# Find connected Free-Wilis
devices = FreeWili.find_all()
if not devices:
    print("No Free-Wili devices found!")
    exit(1)

# Pick the first Free-Wili
device = devices[0]

# We can leave target_name and processor None and it will automatically
# figure out where to send the file.
device.send_file(my_fwi_file, None, None).expect("Failed to upload file")
device.send_file(my_wasm_file, None, None).expect("Failed to upload file")
device.run_script(my_wasm_file.name).expect("Failed to run script")
