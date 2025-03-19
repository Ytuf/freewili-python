"""Test code for freewili.fw module."""

import pytest

from freewili.fw import FileMap
from freewili.serial_util import FreeWiliProcessorType


def test_file_mappings() -> None:
    """Test file mapping."""
    known_maps = {
        "wasm": (FreeWiliProcessorType.Main, "/scripts", "WASM binary"),
        "wsm": (FreeWiliProcessorType.Main, "/scripts", "WASM binary"),
        "sub": (FreeWiliProcessorType.Display, "/radio", "Radio file"),
        "fwi": (FreeWiliProcessorType.Display, "/images", "Image file"),
    }

    for ext, values in known_maps.items():
        map = FileMap.from_ext(ext)
        assert map.extension == ext
        assert map.processor == values[0]
        assert map.directory == values[1]
        assert map.description == values[2]

    with pytest.raises(ValueError, match="Extension 'failure' is not a known FreeWili file type") as _exc_info:
        FileMap.from_ext(".failure")

    assert FileMap.from_fname(r"C:\dev\My Project\Output\test.wasm") == FileMap.from_ext("wasm")
    assert FileMap.from_fname(r"/home/dev/my_project/test.wasm") == FileMap.from_ext("wasm")
    assert FileMap.from_fname(r"test.wasm") == FileMap.from_ext("wasm")

    assert FileMap.from_ext("wasm").to_path("test.wasm") == "/scripts/test.wasm"
    assert FileMap.from_ext("wasm").to_path("/some/random/path/test.wasm") == "/scripts/test.wasm"


if __name__ == "__main__":
    import pytest

    pytest.main(
        args=[
            __file__,
            "--verbose",
        ]
    )
