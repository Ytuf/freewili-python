"""Tests for freewili.cli_convert module."""

from unittest.mock import patch

from result import Err, Ok

from freewili.cli_convert import main


class TestMain:
    """Test cases for the main function."""

    def test_main_successful_conversion(self) -> None:
        """Test successful image conversion via CLI."""
        test_args = ["fwi-convert", "-i", "input.png", "-o", "output.fwi"]

        with (
            patch("sys.argv", test_args),
            patch("freewili.image.convert", return_value=Ok("Conversion successful")) as mock_convert,
            patch("builtins.print") as mock_print,
        ):
            main()

            mock_convert.assert_called_once_with("input.png", "output.fwi")
            mock_print.assert_called_once_with("Conversion successful")

    def test_main_conversion_failure(self) -> None:
        """Test handling of conversion failure via CLI."""
        test_args = ["fwi-convert", "-i", "input.png", "-o", "output.fwi"]

        with patch("sys.argv", test_args), patch("freewili.image.convert", return_value=Err("Conversion failed")):
            try:
                main()
                raise AssertionError("Should have raised SystemExit")
            except SystemExit as e:
                assert e.code == 1  # Error exit code

    def test_main_missing_input_argument(self) -> None:
        """Test error handling when input argument is missing."""
        test_args = ["fwi-convert", "-o", "output.fwi"]

        with patch("sys.argv", test_args), patch("sys.stderr"):  # Suppress argparse error output
            try:
                main()
                raise AssertionError("Should have raised SystemExit")
            except SystemExit as e:
                assert e.code == 2  # argparse error code

    def test_main_missing_output_argument(self) -> None:
        """Test error handling when output argument is missing."""
        test_args = ["fwi-convert", "-i", "input.png"]

        with patch("sys.argv", test_args), patch("sys.stderr"):  # Suppress argparse error output
            try:
                main()
                raise AssertionError("Should have raised SystemExit")
            except SystemExit as e:
                assert e.code == 2  # argparse error code

    def test_main_version_argument(self) -> None:
        """Test version argument displays version information."""
        test_args = ["fwi-convert", "--version"]

        with (
            patch("sys.argv", test_args),
            patch("importlib.metadata.version", return_value="1.0.0"),
            patch("sys.stdout"),
        ):  # Suppress version output
            try:
                main()
                raise AssertionError("Should have raised SystemExit")
            except SystemExit as e:
                assert e.code == 0  # Normal exit for version display

    def test_main_with_pathlib_paths(self) -> None:
        """Test that string arguments are passed correctly to convert function."""
        test_args = ["fwi-convert", "-i", "/path/to/input.png", "-o", "/path/to/output.fwi"]

        with (
            patch("sys.argv", test_args),
            patch("freewili.image.convert", return_value=Ok("Success")) as mock_convert,
            patch("builtins.print"),
        ):
            main()

            # Verify arguments are passed as strings (argparse provides strings)
            mock_convert.assert_called_once_with("/path/to/input.png", "/path/to/output.fwi")
