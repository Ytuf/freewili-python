"""Test code for freewili.types module."""

from freewili.types import (
    GPIO_MAP,
    ButtonColor,
    ButtonData,
    EventData,
    EventType,
    FreeWiliProcessorType,
    IOMenuCommand,
    Radio1Data,
)


def test_processor_type() -> None:
    """Test processor type for ABI breakage."""
    assert FreeWiliProcessorType.Main.value == 1
    assert FreeWiliProcessorType.Display.value == 2
    assert FreeWiliProcessorType.FTDI.value == 3
    assert FreeWiliProcessorType.Unknown.value == 4


def test_processor_type_str() -> None:
    """Test processor type string representation."""
    assert str(FreeWiliProcessorType.Main) == "Main"
    assert str(FreeWiliProcessorType.Display) == "Display"
    assert str(FreeWiliProcessorType.FTDI) == "FTDI"
    assert str(FreeWiliProcessorType.Unknown) == "Unknown"


def test_button_color() -> None:
    """Test ButtonColor enum values."""
    assert ButtonColor.Unknown.value == 1
    assert ButtonColor.White.value == 2
    assert ButtonColor.Yellow.value == 3
    assert ButtonColor.Green.value == 4
    assert ButtonColor.Blue.value == 5
    assert ButtonColor.Red.value == 6


def test_gpio_map() -> None:
    """Test GPIO_MAP constants."""
    assert GPIO_MAP[8] == "GPIO8/UART1_Tx_OUT"
    assert GPIO_MAP[9] == "GPIO9/UART1_Rx_IN"
    assert GPIO_MAP[16] == "GPIO16/I2C0 SDA"
    assert GPIO_MAP[17] == "GPIO17/I2C0 SCL"
    assert GPIO_MAP[25] == "GPIO25/GPIO25_OUT"

    # Test that all expected GPIO pins are present
    expected_pins = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 25, 26, 27]
    for pin in expected_pins:
        assert pin in GPIO_MAP


def test_io_menu_command() -> None:
    """Test IOMenuCommand enum."""
    # Test specific enum values exist
    assert hasattr(IOMenuCommand, "High")
    assert hasattr(IOMenuCommand, "Low")
    assert hasattr(IOMenuCommand, "Toggle")
    assert hasattr(IOMenuCommand, "Get")

    # Test from_string method
    high_cmd = IOMenuCommand.from_string("HIGH")
    assert high_cmd == IOMenuCommand.High


def test_event_data_base_class() -> None:
    """Test EventData base class."""
    # Test that from_string raises NotImplementedError
    try:
        EventData.from_string("test")
        raise AssertionError("Should have raised NotImplementedError")
    except NotImplementedError as e:
        assert "from_string() must be implemented in subclasses" in str(e)


def test_button_data() -> None:
    """Test ButtonData class."""
    # Test ButtonData creation with proper format (5 boolean values as "0" or "1")
    button_data = ButtonData.from_string("0 1 0 0 1")
    assert button_data.gray is False
    assert button_data.yellow is True
    assert button_data.green is False
    assert button_data.blue is False
    assert button_data.red is True


def test_radio1_data() -> None:
    """Test Radio1Data class."""
    # Test Radio1Data creation
    radio_data = Radio1Data.from_string("RADIO1 test_message")
    assert hasattr(radio_data, "data")


def test_event_type() -> None:
    """Test EventType enum."""
    # Test that EventType has expected values
    assert hasattr(EventType, "Radio1")
    assert hasattr(EventType, "GPIO")
    assert hasattr(EventType, "Button")


if __name__ == "__main__":
    import pytest

    pytest.main(
        args=[
            __file__,
            "--verbose",
        ]
    )
