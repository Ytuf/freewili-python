"""Tests for freewili.image module."""

import pathlib
import struct
import tempfile
from unittest.mock import MagicMock, mock_open, patch

from freewili.image import convert


class TestConvert:
    """Test cases for the convert function."""

    def test_convert_success_no_transparency(self) -> None:
        """Test successful conversion of image without transparency."""
        # Create a mock image
        mock_image = MagicMock()
        mock_image.size = (2, 2)  # 2x2 image

        # Mock pixel data without transparency (RGB)
        mock_pix = {
            (0, 0): (255, 0, 0),  # Red pixel
            (1, 0): (0, 255, 0),  # Green pixel
            (0, 1): (0, 0, 255),  # Blue pixel
            (1, 1): (255, 255, 255),  # White pixel
        }
        mock_image.load.return_value = mock_pix

        with patch("freewili.image.Image.open", return_value=mock_image), patch("builtins.open", mock_open()):
            input_path = pathlib.Path("test.png")
            output_path = pathlib.Path("test.fwi")

            result = convert(input_path, output_path)

            assert result.is_ok()
            assert "converted to FreeWili image file" in result.unwrap()

    def test_convert_success_with_transparency(self) -> None:
        """Test successful conversion of image with transparency."""
        mock_image = MagicMock()
        mock_image.size = (1, 1)  # 1x1 image

        # Mock pixel data with transparency (RGBA)
        mock_pix = {
            (0, 0): (255, 0, 0, 128)  # Red pixel with transparency
        }
        mock_image.load.return_value = mock_pix

        with (
            patch("freewili.image.Image.open", return_value=mock_image),
            patch("builtins.open", mock_open()) as mock_file,
        ):
            input_path = pathlib.Path("test.png")
            output_path = pathlib.Path("test.fwi")

            result = convert(input_path, output_path)

            assert result.is_ok()
            mock_file.assert_called_once_with(output_path, "wb")

    def test_convert_transparent_pixel(self) -> None:
        """Test conversion of fully transparent pixel."""
        mock_image = MagicMock()
        mock_image.size = (1, 1)

        # Mock pixel data with full transparency
        mock_pix = {
            (0, 0): (255, 0, 0, 0)  # Fully transparent pixel
        }
        mock_image.load.return_value = mock_pix

        with (
            patch("freewili.image.Image.open", return_value=mock_image),
            patch("builtins.open", mock_open()),
        ):
            input_path = pathlib.Path("test.png")
            output_path = pathlib.Path("test.fwi")

            result = convert(input_path, output_path)

            assert result.is_ok()

    def test_convert_image_open_failure(self) -> None:
        """Test handling of image opening failure."""
        with patch("freewili.image.Image.open", side_effect=Exception("Cannot open image")):
            input_path = pathlib.Path("nonexistent.png")
            output_path = pathlib.Path("test.fwi")

            result = convert(input_path, output_path)

            assert result.is_err()
            error_msg = result.unwrap_err()
            assert "Fail to open png or jpg file" in error_msg
            assert "Cannot open image" in error_msg

    def test_convert_output_file_write_failure(self) -> None:
        """Test handling of output file write failure."""
        mock_image = MagicMock()
        mock_image.size = (1, 1)

        with (
            patch("freewili.image.Image.open", return_value=mock_image),
            patch("builtins.open", side_effect=Exception("Cannot write file")),
        ):
            input_path = pathlib.Path("test.png")
            output_path = pathlib.Path("readonly.fwi")

            result = convert(input_path, output_path)

            assert result.is_err()
            error_msg = result.unwrap_err()
            assert "Can't write the file" in error_msg
            assert "Cannot write file" in error_msg

    def test_convert_header_format(self) -> None:
        """Test that the FWI header is written correctly."""
        mock_image = MagicMock()
        mock_image.size = (2, 3)  # 2x3 image

        mock_pix = {
            (0, 0): (0, 0, 0),
            (1, 0): (0, 0, 0),
            (0, 1): (0, 0, 0),
            (1, 1): (0, 0, 0),
            (0, 2): (0, 0, 0),
            (1, 2): (0, 0, 0),
        }
        mock_image.load.return_value = mock_pix

        with patch("freewili.image.Image.open", return_value=mock_image):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                input_path = pathlib.Path("test.png")
                output_path = pathlib.Path(tmp_file.name)

                result = convert(input_path, output_path)
                assert result.is_ok()

                # Read back the header to verify format
                with open(output_path, "rb") as f:
                    # Header ID: "FW01IMG\0"
                    header_id = f.read(8)
                    assert header_id == b"FW01IMG\0"

                    # Flags (4 bytes)
                    flags = struct.unpack("<I", f.read(4))[0]
                    assert flags == 1

                    # Total pixel count (4 bytes)
                    pixel_count = struct.unpack("<I", f.read(4))[0]
                    assert pixel_count == 6  # 2 * 3

                    # Width (2 bytes)
                    width = struct.unpack("<h", f.read(2))[0]
                    assert width == 2

                    # Height (2 bytes)
                    height = struct.unpack("<h", f.read(2))[0]
                    assert height == 3

    def test_convert_color_conversion(self) -> None:
        """Test RGB to 16-bit color conversion."""
        mock_image = MagicMock()
        mock_image.size = (1, 1)

        # Test with pure red color (255, 0, 0)
        mock_pix = {(0, 0): (255, 0, 0)}
        mock_image.load.return_value = mock_pix

        with patch("freewili.image.Image.open", return_value=mock_image):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                input_path = pathlib.Path("test.png")
                output_path = pathlib.Path(tmp_file.name)

                result = convert(input_path, output_path)
                assert result.is_ok()

                # Read the pixel data (skip 24-byte header)
                with open(output_path, "rb") as f:
                    f.seek(24)  # Skip header
                    pixel_data = f.read(2)  # Read one 16-bit pixel
                    pixel_value = struct.unpack("<H", pixel_data)[0]

                    # Pure red should convert to a non-zero value
                    assert pixel_value > 0
