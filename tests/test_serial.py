"""Test code for freewili.serial module."""

from freewili.serial import FreeWiliProcessorType


def test_processor_type() -> None:
    """Test processor type for ABI breakage."""
    assert FreeWiliProcessorType.Unknown.value == 1
    assert FreeWiliProcessorType.Main.value == 2
    assert FreeWiliProcessorType.Display.value == 3
