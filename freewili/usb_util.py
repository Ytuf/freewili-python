"""USB helper functions to interface with a Free-Wili."""

import sys
from dataclasses import dataclass

import usb

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import platform

if platform.system().lower() == "windows":
    import warnings
    warnings.filterwarnings("ignore")
    from pyusb_chain.usb_tree_view_tool import UsbTreeViewTool

# FreeWili Black FTDI VendorID
USB_VID_FW_FTDI: int = 0x0403
# FreeWili Black FTDI ProductID
USB_PID_FW_FTDI: int = 0x6014

# Raspberry Pi Vendor ID
USB_VID_FW_RPI: int = 0x2E8A
# Raspberry Pi Pico SDK CDC UART Product ID
USB_PID_FW_RPI_CDC_PID: int = 0x000A
# Raspberry Pi Pico SDK UF2 Product ID
USB_PID_FW_RPI_UF2_PID: int = 0x0003


@dataclass(frozen=True)
class USBLocationInfo:
    """USB Location Information for a specific device."""

    # USB Vendor ID
    vendor_id: int
    # USB Product ID
    product_id: int
    # USB bus location
    bus: int
    # USB address location
    address: int
    # USB product name
    name: None | str
    # USB serial number
    serial: str
    # Parent USB device this is attached to (HUB)
    parent: None | Self

    def __str__(self) -> str:
        return (
            f"{self.name} {self.serial} "
            f"[{self.vendor_id:#04x}:{self.product_id:#04x}]"
            f"[{self.bus}:{self.address}]"
        )

    @classmethod
    def from_libusb(cls, dev: usb.core.Device) -> Self:
        """Create a USBLocationInfo based on libusb object."""
        # Get the serial number
        try:
            dev._langids = (1033,)
            serial_number: str = dev.serial_number
        except Exception as _ex:
            serial_number = ""
        # Get the product name
        try:
            product: str = dev.product
        except Exception as _ex:
            product = ""
        # Try to query the parent device
        try:
            parent = None
            if dev.parent:
                parent = cls.from_libusb(dev.parent)
        except Exception as ex:
            print(f"Exception: from_lubusb(): {ex}")
            parent = None
        # Create our USBLocationInfo
        usb_location_info = cls(dev.idVendor, dev.idProduct, dev.bus, dev.address, product, serial_number, parent)
        return usb_location_info


def find_all(vid: None | int = None, pid: None | int = None) -> tuple[USBLocationInfo, ...]:
    """Find all USB devices attached to Host from a given USB VID and PID.

    Parameters:
    ----------
        vid: None | int
            USB Vendor ID to search for
        pid: None | int
            USB Product ID to search for

    Returns:
    -------
        tuple[USBLocationInfo]:
            Tuple of USBLocationInfo

    Raises:
    -------
        None
    """
    # We can't pass idVendor and idProduct in as None because it won't
    # match anything, so lets not include it if its None
    kwargs = {}
    if vid:
        kwargs["idVendor"] = vid
    if pid:
        kwargs["idProduct"] = pid
    if platform.system().lower() == "windows":
        usb_devices = list(usb.core.find(**kwargs, find_all=True))
        # libusb on windows doesn't support the serial so we are going to grab it from usbview
        # and directly modify the libusb class.
        UsbTreeViewTool()
        tool = UsbTreeViewTool()
        tool.scan()
        win_devices = tool.filter(None)
        # ['1-1', '', 'USB Composite Device - 2× Camera', None, 11]
        # ['2-1-1', 'COM6', 'USB Composite Device - COM6', 'E463A8574B103A35', 19]
        # ['2-1-2', 'COM5', 'USB Composite Device - COM5', 'E463A8574B423835', 20]
        # ['2-1-3', 'COM7', 'USB Serial Converter - COM7', 'FW5275', 21]
        # ['3-1', '', 'USB Composite Device - Mouse, Keyboard, 2× HID', '127C395F3038', 12]
        # ['3-2-1', 'COM3', 'USB Composite Device - COM3', 'E463A8574B133839', 14]
        # ['3-2-2', 'COM4', 'USB Composite Device - COM4', 'E463A8574B5E3839', 15]
        # ['3-2-3', 'COM8', 'USB Serial Converter - COM8', 'FW5491', 22]
        # ['3-3-1', '', 'Qualcomm FastConnect 6900 Bluetooth Adapter', None, 0]
        # ['3-5', '', 'Goodix MOC Fingerprint', None, 0]
        for usb_device in usb_devices:
            # for some reason the port_number seems wrong but the bus reflects
            # the correct number here
            usb_port_numbers = [usb_device.bus - 1]
            usb_port_numbers.extend(usb_device.port_numbers)
            matched = False
            for device in win_devices:
                data = device.export_data(True)[0]
                loc_id = data[0]
                port_numbers = [int(x) for x in loc_id.split("-")]
                _com_port_name = data[1]
                name = data[2]
                serial = data[3]
                _address = data[4]

                if usb_port_numbers == port_numbers:
                    usb_device._serial_number = serial
                    usb_device._product = name
                    matched = True
                    break
            if matched:
                continue
            # Lets do it again, we didn't match. don't decrement bus by one this time...
            usb_port_numbers = [usb_device.bus]
            usb_port_numbers.extend(usb_device.port_numbers)
            matched = False
            for device in win_devices:
                data = device.export_data(True)[0]
                loc_id = data[0]
                port_numbers = [int(x) for x in loc_id.split("-")]
                _com_port_name = data[1]
                name = data[2]
                serial = data[3]
                _address = data[4]

                if usb_port_numbers == port_numbers:
                    usb_device._serial_number = serial
                    usb_device._product = name
                    matched = True
                    break
            if not matched:
                raise RuntimeError("Failed to match device.")
    else:
        usb_devices = list(usb.core.find(**kwargs, find_all=True))
    devices: list[USBLocationInfo] = []
    for dev in usb_devices:
        devices.append(USBLocationInfo.from_libusb(dev))
    return tuple(devices)


if __name__ == "__main__":
    ftdi_devices = find_all(vid=USB_VID_FW_FTDI, pid=USB_PID_FW_FTDI)
    for dev in ftdi_devices:
        print(dev)
    fw_devices = find_all(vid=USB_VID_FW_RPI)
    for dev in fw_devices:
        print(dev)
