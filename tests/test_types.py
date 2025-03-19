"""Test code for freewili.types module."""

from freewili.serial_util import FreeWiliProcessorType


def test_processor_type() -> None:
    """Test processor type for ABI breakage."""
    assert FreeWiliProcessorType.Main.value == 1
    assert FreeWiliProcessorType.MainUF2.value == 2
    assert FreeWiliProcessorType.Display.value == 3
    assert FreeWiliProcessorType.DisplayUF2.value == 4
    assert FreeWiliProcessorType.FTDI.value == 5
    assert FreeWiliProcessorType.Unknown.value == 6


if __name__ == "__main__":
    import pytest

    pytest.main(
        args=[
            __file__,
            "--verbose",
        ]
    )
