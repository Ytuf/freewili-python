"""Test ResponseFrame."""

import numpy as np

from freewili.framing import ResponseFrame, ResponseFrameType


def test_response_frame() -> None:
    """Test ResponseFrame decoding."""
    response_frame = ResponseFrame.from_raw(r"[i\w 1831A98807457841 4 Invalid 0]", strict=False).expect(
        "Failed to decode frame"
    )
    assert response_frame.rf_type == ResponseFrameType.Standard
    assert response_frame.rf_type_data == r"i\w"
    assert response_frame.timestamp == 1743360932471732289
    assert response_frame.seq_number == 4
    assert response_frame.response == "Invalid"
    assert response_frame.success == 0
    assert not response_frame.is_ok()
    assert response_frame.response_as_bytes().is_err()
    assert response_frame.timestamp_as_datetime().expect("Failed to get timestamp as datetime") == np.datetime64(
        1743360932471732289, "ns"
    )

    response_frame = ResponseFrame.from_raw(r"[*UART1 1831A98807457841 0 Failed 0]", strict=False).expect(
        "Failed to decode frame"
    )
    assert response_frame.rf_type == ResponseFrameType.Event
    assert response_frame.rf_type_data == r"UART1"
    assert response_frame.timestamp == 1743360932471732289
    assert response_frame.seq_number == 0
    assert response_frame.response == "Failed"
    assert response_frame.success == 0
    assert not response_frame.is_ok()
    assert response_frame.response_as_bytes().is_err()

    # Real I2C Read response frame v43
    response_frame = ResponseFrame.from_raw(r"[i\r 1831A98807457841 0 3F 1]", strict=False).expect(
        "Failed to decode frame"
    )
    assert response_frame.rf_type == ResponseFrameType.Standard
    assert response_frame.rf_type_data == r"i\r"
    assert response_frame.timestamp == 1743360932471732289
    assert response_frame.seq_number == 0
    assert response_frame.response == "3F"
    assert response_frame.success == 1
    assert response_frame.is_ok()
    assert response_frame.response_as_bytes().is_ok()
    assert response_frame.response_as_bytes().unwrap() == bytes(
        [
            0x3F,
        ]
    )

    # Real I2C Poll response frame v43
    response_frame = ResponseFrame.from_raw(r"[i\p 1831A98807457841 16 2 30 6B 1]", strict=False).expect(
        "Failed to decode frame"
    )
    assert response_frame.rf_type == ResponseFrameType.Standard
    assert response_frame.rf_type_data == r"i\p"
    assert response_frame.timestamp == 1743360932471732289
    assert response_frame.seq_number == 16
    assert response_frame.response == "2 30 6B"
    assert response_frame.success == 1
    assert response_frame.is_ok()
    assert response_frame.response_as_bytes().is_ok()
    assert response_frame.response_as_bytes().unwrap() == bytes([2, 0x30, 0x6B])

    # Real I2C Poll response no hardware v43
    response_frame = ResponseFrame.from_raw(r"[i\p 1831A98807457841 2 0 1]", strict=False).expect(
        "Failed to decode frame"
    )
    assert response_frame.rf_type == ResponseFrameType.Standard
    assert response_frame.rf_type_data == r"i\p"
    assert response_frame.timestamp == 1743360932471732289
    assert response_frame.seq_number == 2
    assert response_frame.response == "0"
    assert response_frame.success == 1
    assert response_frame.is_ok()
    assert response_frame.response_as_bytes().is_ok()
    assert response_frame.response_as_bytes().unwrap() == bytes(
        [
            0,
        ]
    )


if __name__ == "__main__":
    import pytest

    pytest.main(
        args=[
            __file__,
            "--verbose",
        ]
    )
