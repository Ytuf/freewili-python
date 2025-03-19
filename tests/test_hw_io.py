"""Test I2C functionality on a FreeWili."""

import pytest

from freewili import FreeWili
from freewili.framing import ResponseFrameType
from freewili.serial_util import IOMenuCommand


@pytest.mark.skipif("len(FreeWili.find_all()) == 0")
def test_hw_io() -> None:
    """Test IO on a FreeWili."""
    device = FreeWili.find_all()[0]
    device.stay_open = True

    try:
        # Set IO low
        response_frame = device.set_io(25, IOMenuCommand.Low).expect("Failed to set IO low")
        assert response_frame.rf_type == ResponseFrameType.Standard
        assert response_frame.rf_type_data == r"o\l"
        assert response_frame.timestamp != 0
        assert response_frame.response == "Ok"
        assert response_frame.is_ok()
        # Check to make sure IO is low
        assert device.get_io().expect("Failed to get IO")[25] == 0
        # Set IO High
        response_frame = device.set_io(25, IOMenuCommand.High).expect("Failed to set IO high")
        assert response_frame.rf_type == ResponseFrameType.Standard
        assert response_frame.rf_type_data == r"o\s"
        assert response_frame.timestamp != 0
        assert response_frame.response == "Ok"
        assert response_frame.is_ok()
        # Check to make sure IO is high
        assert device.get_io().expect("Failed to get IO")[25] == 1
        # Set IO toggle to low
        response_frame = device.set_io(25, IOMenuCommand.Toggle).expect("Failed to set IO high")
        assert response_frame.rf_type == ResponseFrameType.Standard
        assert response_frame.rf_type_data == r"o\t"
        assert response_frame.timestamp != 0
        assert response_frame.response == "Ok"
        assert response_frame.is_ok()
        # Check to make sure IO is low
        assert device.get_io().expect("Failed to get IO")[25] == 0
    finally:
        device.close()


if __name__ == "__main__":
    import pytest

    pytest.main(
        args=[
            __file__,
            "--verbose",
        ]
    )
