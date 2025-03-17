"""For Interfacing to Free-Wili Devices."""

import pathlib
from collections import OrderedDict
from dataclasses import dataclass
from typing import Self

from result import Err, Result

import freewili
from freewili import usb_util
from freewili.serial_util import FreeWiliSerial
from freewili.types import FreeWiliProcessorType
from freewili.usb_util import USB_VID_FW_FTDI, USB_VID_FW_RPI, USBLocationInfo

# USB Locations:
# first address = FTDI
FTDI_HUB_LOC_INDEX = 2
# second address = Display
DISPLAY_HUB_LOC_INDEX = 1
# third address = Main
MAIN_HUB_LOC_INDEX = 0


@dataclass(frozen=True)
class FreeWiliProcessorInfo:
    """Processor USB and Serial Port info of the Free-Wili."""

    processor_type: FreeWiliProcessorType
    usb_info: USBLocationInfo
    serial_info: None | FreeWiliSerial

    def __str__(self) -> str:
        if self.serial_info:
            return f"{self.serial_info}"
        return f"{self.processor_type}: {self.usb_info}"


@dataclass(frozen=True)
class FreeWiliInfo:
    """FreeWili Info."""

    serial_number: str
    processors: tuple[FreeWiliProcessorInfo, ...]


class FreeWili:
    """Free-Wili device used to access FTDI and serial functionality."""

    def __init__(self, info: FreeWiliInfo):
        self.info = info

    def __str__(self) -> str:
        return f"Free-Wili {self.info.serial_number}"

    def _get_processor(self, processor_type: FreeWiliProcessorType) -> FreeWiliProcessorInfo:
        for processor in self.info.processors:
            if processor.processor_type == processor_type:
                return processor
        raise IndexError(f"Processor {processor_type} not found for {self}")

    @property
    def ftdi(self) -> FreeWiliProcessorInfo:
        """Get FTDI processor."""
        return self._get_processor(FreeWiliProcessorType.FTDI)

    @property
    def main(self) -> FreeWiliProcessorInfo:
        """Get Main processor."""
        return self._get_processor(FreeWiliProcessorType.Main)

    @property
    def display(self) -> FreeWiliProcessorInfo:
        """Get Display processor."""
        return self._get_processor(FreeWiliProcessorType.Display)

    @classmethod
    def find_all(cls) -> tuple[Self, ...]:
        """Find all Free-Wili devices attached to the host.

        Parameters:
        ----------
            None

        Returns:
        -------
            tuple[FreeWili, ...]:
                Tuple of FreeWili devices.

        Raises:
        -------
            None
        """
        all_usb = usb_util.find_all(vid=USB_VID_FW_FTDI) + usb_util.find_all(vid=USB_VID_FW_RPI)
        # sort by bus
        usb_buses = OrderedDict({})
        for usb_dev in all_usb:
            if usb_dev.bus not in usb_buses:
                usb_buses[usb_dev.bus] = [
                    usb_dev,
                ]
            else:
                bus = usb_buses[usb_dev.bus]
                bus.append(usb_dev)
                # Sort all the addresses
                bus = sorted(bus, key=lambda x: x.address)
                usb_buses[usb_dev.bus] = bus
        # Sort all the bus numbers
        usb_buses = OrderedDict(sorted(usb_buses.items()))
        # get all the serial ports
        serial_ports = freewili.serial_util.find_all()

        freewilis = []
        for _bus, usb_devices in usb_buses.items():
            ftdi_usb: USBLocationInfo = usb_devices[FTDI_HUB_LOC_INDEX]
            main_usb: USBLocationInfo = usb_devices[MAIN_HUB_LOC_INDEX]
            display_usb: USBLocationInfo = usb_devices[DISPLAY_HUB_LOC_INDEX]
            # match up the serial port to the USB device
            ftdi_serial = None
            main_serial = None
            display_serial = None
            for serial_port in serial_ports:
                # Windows likes to append letters to the end of the serial numbers...
                if serial_port.info.serial.startswith(ftdi_usb.serial):
                    ftdi_serial = serial_port
                if main_usb.serial == serial_port.info.serial:
                    serial_port.info.fw_serial = ftdi_usb.serial
                    main_serial = serial_port
                if display_usb.serial == serial_port.info.serial:
                    serial_port.info.fw_serial = ftdi_usb.serial
                    display_serial = serial_port
            processors = (
                FreeWiliProcessorInfo(FreeWiliProcessorType.FTDI, ftdi_usb, ftdi_serial),
                FreeWiliProcessorInfo(FreeWiliProcessorType.Main, main_usb, main_serial),
                FreeWiliProcessorInfo(FreeWiliProcessorType.Display, display_usb, display_serial),
            )
            serial: str = ftdi_usb.serial if ftdi_usb.serial else "None"
            freewilis.append(FreeWili(FreeWiliInfo(serial, processors)))
        return tuple(freewilis)  # type: ignore

    def send_file(
        self, source_file: str | pathlib.Path, target_name: None | str, processor: None | FreeWiliProcessorType
    ) -> Result[str, str]:
        """Send a file to the FreeWili.

        Arguments:
        ----------
            source_file: pathlib.Path
                Path to the file to be sent.
            target_name: None | str
                Name of the file in the FreeWili. If None, will be determined automatically based on the filename.
            processor: None | FreeWiliProcessorType
                Processor to upload the file to. If None, will be determined automatically based on the filename.

        Returns:
        -------
            Result[str, str]:
                Returns Ok(str) if the command was sent successfully, Err(str) if not.
        """
        try:
            # Auto assign values that are None
            if not target_name:
                target_name = FileMap.from_fname(str(source_file)).to_path(str(source_file))
            if not processor:
                processor = FileMap.from_fname(str(source_file)).processor
        except ValueError as ex:
            return Err(str(ex))
        assert target_name is not None
        assert processor is not None
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.send_file(source_file, target_name)

    def run_script(
        self, file_name: str, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main
    ) -> Result[str, str]:
        """Run a script on the FreeWili.

        Arguments:
        ----------
            file_name: str
                Name of the file in the FreeWili. 8.3 filename limit exists as of V12
            processor: FreeWiliProcessorType
                Processor to upload the file to.

        Returns:
        -------
            Result[str, str]:
                Ok(str) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.run_script(file_name)

    def set_io(
        self: Self, io: int, high: bool, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main
    ) -> Result[str, str]:
        """Set the state of an IO pin to high or low.

        Parameters:
        ----------
            io : int
                The number of the IO pin to set.
            high : bool
                Whether to set the pin to high or low.
            processor: FreeWiliProcessorType
                Processor to set IO on.

        Returns:
        -------
            Result[str, str]:
                Ok(str) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.set_io(io, high)


@dataclass(frozen=True)
class FileMap:
    """Map file extension to processor type and location."""

    # file extension type (ie. .fwi)
    extension: str
    # processor the file should live on
    processor: FreeWiliProcessorType
    # directory the file type
    directory: str
    # description of the file type
    description: str

    @classmethod
    def from_ext(cls, ext: str) -> Self:
        """Creates a FileMap from a file extension.

        Parameters:
        ----------
            ext: str
                File extension (ie. ".wasm"). Not case sensitive.

        Returns:
        --------
            FileMap

        Raises:
        -------
            ValueError:
                If the extension isn't known.
        """
        ext = ext.lstrip(".").lower()
        mappings = {
            "wasm": (FreeWiliProcessorType.Main, "/scripts", "WASM binary"),
            "wsm": (FreeWiliProcessorType.Main, "/scripts", "WASM binary"),
            "sub": (FreeWiliProcessorType.Display, "/radio", "Radio file"),
            "fwi": (FreeWiliProcessorType.Display, "/images", "Image file"),
        }
        if ext not in mappings:
            raise ValueError(f"Extension '{ext}' is not a known FreeWili file type")
        return cls(ext, *mappings[ext])

    @classmethod
    def from_fname(cls, file_name: str) -> Self:
        """Creates a FileMap from a file path.

        Parameters:
        ----------
            file_name: str
                File name (ie. "myfile.wasm"). Not case sensitive. Can contain paths.

        Returns:
        --------
            FileMap

        Raises:
        -------
            ValueError:
                If the extension isn't known.
        """
        fpath = pathlib.Path(file_name)
        return cls.from_ext(fpath.suffix)

    def to_path(self, file_name: str) -> str:
        """Creates a file path from the file_name to upload to the FreeWili.

        Parameters:
        ----------
            file_name: str
                File name (ie. "myfile.wasm"). Not case sensitive. Can contain paths.

        Returns:
        --------
            str
                Full file path intended to be uploaded to a FreeWili

        Raises:
        -------
            ValueError:
                If the extension isn't known.
        """
        fpath = pathlib.Path(file_name)
        return str(pathlib.Path(self.directory) / fpath.name)


if __name__ == "__main__":
    devices = FreeWili.find_all()
    print(f"Found {len(devices)} Free-Wili(s):")
    for i, dev in enumerate(devices):
        print(f"{i}. {dev}")
        ftdi = dev.ftdi
        main = dev.main
        display = dev.display
        print("\tFTDI:   ", ftdi)  # type: ignore
        print("\tMain:   ", main)  # type: ignore
        print("\tDisplay:", display)  # type: ignore
