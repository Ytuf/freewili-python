"""For Interfacing to Free-Wili Devices."""

import pathlib
import platform
import sys
from collections import OrderedDict
from dataclasses import dataclass

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from result import Err, Ok, Result

import freewili
from freewili import usb_util
from freewili.framing import ResponseFrame
from freewili.serial_util import FreeWiliSerial, IOMenuCommand
from freewili.types import FreeWiliProcessorType
from freewili.usb_util import (
    USB_PID_FW_FTDI,
    USB_PID_FW_HUB,
    USB_PID_FW_RPI_UF2_PID,
    USB_VID_FW_FTDI,
    USB_VID_FW_HUB,
    USB_VID_FW_RPI,
    USBLocationInfo,
)

# USB Locations:
# first address = FTDI
FTDI_HUB_LOC_INDEX = 2
# second address = Display
DISPLAY_HUB_LOC_INDEX = 1
# third address = Main
MAIN_HUB_LOC_INDEX = 0

# This maps the actual GPIO exposed on the connector, all others not
# listed here are internal to the processor.
GPIO_MAP = {
    8: "GPIO8/UART1_Tx_OUT",
    9: "GPIO9/UART1_Rx_IN",
    10: "GPIO10/UART1_CTS_IN",
    11: "GPIO11/UART1_RTS_OUT",
    12: "GPIO12/SPI1_Rx_IN",
    13: "GPIO13/SPI1_CS_OUT",
    14: "GPIO14/SPI1_SCLK_OUT",
    15: "GPIO15/SPI1_Tx_OUT",
    16: "GPIO16/I2C0 SDA",
    17: "GPIO17/I2C0 SCL",
    25: "GPIO25/GPIO25_OUT",
    26: "GPIO26/GPIO26_IN",
    27: "GPIO27/GPIO_27_OUT",
}


@dataclass(frozen=True)
class FreeWiliProcessorInfo:
    """Processor USB and Serial Port info of the Free-Wili."""

    processor_type: FreeWiliProcessorType
    usb_info: None | USBLocationInfo
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
        self._stay_open = False

    def __str__(self) -> str:
        return f"Free-Wili {self.info.serial_number}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.info.serial_number}>"

    def _get_processor(self, processor_type: FreeWiliProcessorType) -> FreeWiliProcessorInfo:
        for processor in self.info.processors:
            if processor.processor_type == processor_type:
                if processor.serial_info:
                    processor.serial_info.stay_open = self.stay_open
                return processor
        raise IndexError(f"Processor {processor_type} not found for {self}")

    @property
    def ftdi(self) -> None | FreeWiliProcessorInfo:
        """Get FTDI processor."""
        try:
            return self._get_processor(FreeWiliProcessorType.FTDI)
        except IndexError:
            return None

    @property
    def main(self) -> None | FreeWiliProcessorInfo:
        """Get Main processor."""
        try:
            return self._get_processor(FreeWiliProcessorType.Main)
        except IndexError:
                return None

    @property
    def display(self) -> None | FreeWiliProcessorInfo:
        """Get Display processor."""
        try:
            return self._get_processor(FreeWiliProcessorType.Display)
        except IndexError:
            return None

    @property
    def stay_open(self) -> bool:
        """Keep serial port open, if True.

        Returns:
            bool
        """
        return self._stay_open

    @stay_open.setter
    def stay_open(self, value: bool) -> None:
        self._stay_open = value

    def close(self, restore_menu: bool = True) -> None:
        """Close the serial port. Use in conjunction with stay_open.

        Arguments:
        ----------
            restore_menu: bool
                Restore the menu functionality before close

        Returns:
        -------
            None
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(FreeWiliProcessorType.Main).serial_info
        if serial_info:
            serial_info.close()
        serial_info = self._get_processor(FreeWiliProcessorType.Display).serial_info
        if serial_info:
            serial_info.close()

    @classmethod
    def find_first(cls) -> Result[Self, str]:
        """Find first Free-Wili device attached to the host.

        Parameters:
        ----------
            None

        Returns:
        -------
            Result[FreeWili, str]:
                Ok(FreeWili) if successful, Err(str) otherwise.

        Raises:
        -------
            None
        """
        try:
            devices = cls.find_all()
            if not devices:
                return Err("No FreeWili devices found!")
            return Ok(devices[0])
        except Exception as ex:
            return Err(str(ex))

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
        hubs = usb_util.find_all(USB_VID_FW_HUB, USB_PID_FW_HUB, False, True)
        if not hubs:
            # no hubs found
            return ()
        # Find all devices we should have on the hub
        all_usb = usb_util.find_all(USB_VID_FW_FTDI, USB_PID_FW_FTDI, True, False) + usb_util.find_all(
            USB_VID_FW_RPI, None, True, False
        )
        fw_hubs = []
        for hub in hubs:
            usb_devices = OrderedDict({})
            for usb in all_usb:
                if usb.parent != hub:
                    continue
                usb_devices[usb.port_number] = usb
            fw_hubs.append(usb_devices)

        serial_ports = freewili.serial_util.find_all()
        freewilis = []
        for fw_hub in fw_hubs:
            indexes = sorted(fw_hub.keys())
            try:
                main_usb: None | USBLocationInfo = fw_hub[indexes[MAIN_HUB_LOC_INDEX]]
            except IndexError:
                main_usb = None
            try:
                display_usb: None | USBLocationInfo = fw_hub[indexes[DISPLAY_HUB_LOC_INDEX]]
            except IndexError:
                display_usb = None
            try:
                ftdi_usb: None | USBLocationInfo = fw_hub[indexes[FTDI_HUB_LOC_INDEX]]
            except IndexError:
                ftdi_usb = None

            # match up the serial port to the USB device
            ftdi_serial = None
            main_serial = None
            display_serial = None
            for serial_port in serial_ports:
                # Windows likes to append letters to the end of the serial numbers...
                if ftdi_usb and serial_port.info.serial.startswith(ftdi_usb.serial):
                    ftdi_serial = serial_port
                if main_usb and main_usb.serial == serial_port.info.serial:
                    serial_port.info.fw_serial = ftdi_usb.serial if ftdi_usb else None
                    main_serial = serial_port
                if display_usb and display_usb.serial == serial_port.info.serial:
                    serial_port.info.fw_serial = ftdi_usb.serial if ftdi_usb else None
                    display_serial = serial_port
            # Get main processor based on PID
            main_processor_type = FreeWiliProcessorType.Main
            if main_usb and main_usb.vendor_id == USB_PID_FW_RPI_UF2_PID:
                main_processor_type = FreeWiliProcessorType.MainUF2
            elif main_usb is None:
                main_processor_type = FreeWiliProcessorType.Unknown
            # Get display processor based on PID
            display_processor_type = FreeWiliProcessorType.Display
            if display_usb and display_usb.vendor_id == USB_PID_FW_RPI_UF2_PID:
                display_processor_type = FreeWiliProcessorType.DisplayUF2
            elif display_usb is None:
                display_processor_type = FreeWiliProcessorType.Unknown

            processors = (
                FreeWiliProcessorInfo(FreeWiliProcessorType.FTDI, ftdi_usb, ftdi_serial),
                FreeWiliProcessorInfo(main_processor_type, main_usb, main_serial),
                FreeWiliProcessorInfo(display_processor_type, display_usb, display_serial),
            )
            serial = "None"
            if ftdi_usb and ftdi_usb.serial:
                serial = ftdi_usb.serial
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

    def get_io(self, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main) -> Result[tuple[int], str]:
        """Get all the IO values.

        Parameters:
        ----------
            processor: FreeWiliProcessorType
                Processor to set IO on.

        Returns:
        -------
            Result[tuple[int], str]:
                Ok(tuple[int]) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.get_io()

    def set_io(
        self: Self,
        io: int,
        menu_cmd: IOMenuCommand,
        pwm_freq: None | int = None,
        pwm_duty: None | int = None,
        processor: FreeWiliProcessorType = FreeWiliProcessorType.Main,
    ) -> Result[ResponseFrame, str]:
        """Set the state of an IO pin to high or low.

        Parameters:
        ----------
            io : int
                The number of the IO pin to set.
            menu_cmd : IOMenuCommand
                Whether to set the pin to high, low, toggle, or pwm.
            pwm_freq: None | int
                PWM frequency in Hertz
            pwm_duty: None | int
                PWM Duty cycle (0-100)
            processor: FreeWiliProcessorType
                Processor to set IO on.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.set_io(io, menu_cmd, pwm_freq, pwm_duty)

    def set_board_leds(
        self: Self,
        io: int,
        red: int,
        green: int,
        blue: int,
        processor: FreeWiliProcessorType = FreeWiliProcessorType.Display,
    ) -> Result[ResponseFrame, str]:
        """Set the GUI RGB LEDs.

        Parameters:
        ----------
            io : int
                The number of the IO pin to set.
            red : int
                Red Color 0-255
            green : int
                Green Color 0-255
            blue : int
                Blue Color 0-255
            processor: FreeWiliProcessorType
                Processor to set LEDs on.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # k) GUI Functions
        # s) Set Board LED [25 100 100 100]
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.set_board_leds(io, red, green, blue)

    def read_i2c(
        self, address: int, register: int, data_size: int, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main
    ) -> Result[ResponseFrame, str]:
        """Write I2C data.

        Parameters:
        ----------
            address : int
                The address to write to.
            register : int
                The register to write to.
            data_size : int
                The number of bytes to read.
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.read_i2c(address, register, data_size)

    def write_i2c(
        self, address: int, register: int, data: bytes, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main
    ) -> Result[ResponseFrame, str]:
        """Write I2C data.

        Parameters:
        ----------
            address : int
                The address to write to.
            register : int
                The register to write to.
            data : bytes
                The data to write.
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.write_i2c(address, register, data)

    def poll_i2c(self, processor: FreeWiliProcessorType = FreeWiliProcessorType.Main) -> Result[ResponseFrame, str]:
        """Write I2C data.

        Parameters:
        ----------
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.poll_i2c()

    def show_gui_image(
        self, fwi_path: str, processor: FreeWiliProcessorType = FreeWiliProcessorType.Display
    ) -> Result[ResponseFrame, str]:  # Result[Tuple[int, ...], str]:
        """Show a fwi image on the display.

        Arguments:
        ----------
            fwi_path: str
                path to the fwi image
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.show_gui_image(fwi_path)

    def show_text_display(
        self, text: str, processor: FreeWiliProcessorType = FreeWiliProcessorType.Display
    ) -> Result[ResponseFrame, str]:  # Result[Tuple[int, ...], str]:
        """Show text on the display.

        Arguments:
        ----------
            text: str
                text to display on screen.
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.show_text_display(text)

    def read_all_buttons(
        self, processor: FreeWiliProcessorType = FreeWiliProcessorType.Display
    ) -> Result[ResponseFrame, str]:  # Result[Tuple[int, ...], str]:
        """Read all the buttons.

        Arguments:
        ----------
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.read_all_buttons()

    def reset_display(
        self, processor: FreeWiliProcessorType = FreeWiliProcessorType.Display
    ) -> Result[ResponseFrame, str]:  # Result[Tuple[int, ...], str]:
        """Reset the display back to the main menu.

        Arguments:
        ----------
            processor: FreeWiliProcessorType
                Processor to use.

        Returns:
        -------
            Result[ResponseFrame, str]:
                Ok(ResponseFrame) if the command was sent successfully, Err(str) if not.
        """
        # Get the FreeWiliSerial and use it
        serial_info = self._get_processor(processor).serial_info
        if not serial_info:
            return Err(f"Serial info not available for {processor}")
        return serial_info.reset_display()


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
            "zio": (FreeWiliProcessorType.Main, "/scripts", "ZoomIO script file"),
            "bit": (FreeWiliProcessorType.Main, "/fpga", "FPGA bit file"),
            "sub": (FreeWiliProcessorType.Display, "/radio", "Radio file"),
            "fwi": (FreeWiliProcessorType.Display, "/images", "Image file"),
            "wav": (FreeWiliProcessorType.Display, "/sounds", "Audio file"),
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
        fpath_str = str(pathlib.Path(self.directory) / fpath.name)
        if platform.system().lower() == "windows":
            fpath_str = fpath_str.replace("\\", "/")
        return fpath_str


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
