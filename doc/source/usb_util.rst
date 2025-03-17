USB Utility Module
================
API for interacting with USB for Free-Wili. This is a low level interface and typically not required.


USB Utils Examples
---------------

.. code-block:: python
    :caption: Search for FreeWilis connected over USB
        
        from freewili.usb_util import find_all, USB_VID_FW_FTDI, USB_PID_FW_FTDI
        
        # Find all FTDI processors
        ftdi_devices = find_all(vid=USB_VID_FW_FTDI, pid=USB_PID_FW_FTDI)
        print(f"Found {len(ftdi_devices)} FTDI FreeWili(s)")
        for device in ftdi_devices:
            print(device)

        # Find all RPi processors
        rpi_devices = find_all(vid=USB_VID_FW_RPI)
        print(f"Found {len(rpi_devices)} RPi FreeWili Processor(s)")
        for device in rpi_devices:
            print(device)


USB util API
-----------------
.. automodule:: freewili.usb_util
   :members:
   :show-inheritance:
   :undoc-members:
