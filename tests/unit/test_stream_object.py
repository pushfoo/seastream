"""
Test the stream object.

"""

import pytest
import pathlib
from itertools import product

from unittest.mock import Mock

from unittest.mock import mock_open
from unittest.mock import patch

from io import BytesIO
from seastream.seastream import SeaStream


@pytest.fixture
def dummy_streams():
    base = Mock(spec=BytesIO)
    stream = SeaStream(base)

    yield (base, stream)


class TestInit:

    def test_passed_stream_no_mode(self, dummy_streams):
        base, stream = dummy_streams
        assert stream.wrapped_stream is base

    def test_invalid_mode_type(self):
        with pytest.raises(TypeError):
            SeaStream("/foo", mode=3)

    def test_invalid_mode_string(self):
        with pytest.raises(ValueError):
            SeaStream("/foo", mode="rw")

    @pytest.mark.parametrize(
        "path,mode",
        list(product(
            ["/foo", pathlib.Path("/foo"), b"/foo"],
            ["ab", "rb", "wb", "wb+", "ab", "ab+"]
        ))
    )
    @patch("builtins.open", new_callable=mock_open)
    def test_valid_base_and_mode(self, mock_file, path, mode):
        s = SeaStream(path, mode)
        mock_file.assert_called_with(path, mode=mode)


class DummySerializable:

    _struct = Mock(size=3)

    @classmethod
    def from_bytes(cls, b):
        return "foo"

    def __bytes__(self):
        return b"foo"


class TestRead:

    def test_int_arg(self, dummy_streams):
        """Normal int arguments are passed transparently to wrapped stream"""
        raw, s = dummy_streams
        s.read(6)
        raw.read.assert_called_once_with(6)

    def test_type_arg(self, dummy_streams):
        """Type args get properly read"""
        raw, s = dummy_streams

        assert s.read(DummySerializable) == "foo"

        raw.read.assert_called_once_with(
            DummySerializable._struct.size
        )

    def test_invalid_type(self, dummy_streams):
        """Error when read is passed something other than a type or int"""
        raw, s = dummy_streams

        with pytest.raises(TypeError):
            s.read("strings are an invalid type")


class TestWrite:

    def test_supported_object(self, dummy_streams):
        """Type instances are converted and written to wrapped stream """
        raw, s = dummy_streams
        raw.write.return_value = 3

        bytes_dunder = DummySerializable()

        assert DummySerializable._struct.size == s.write(bytes_dunder)
        raw.write.assert_called_once_with(b"foo")

    def test_bytelike_objects(self, dummy_streams):
        """Assumed bytes-like written directly to the wrapped stream"""
        raw, s = dummy_streams
        to_write = b"foo"
        raw.write.return_value = len(to_write)

        assert len(to_write) == s.write(to_write)

        raw.write.assert_called_once_with(to_write)


class TestContextManagerCleanup:

    @patch("builtins.open", new_callable=mock_open)
    def test_cleanup_filename(self, mock_file_open):
        """Context manager auto-closes files opened from paths"""

        with SeaStream("foo") as s:
            pass

        mock_file_open.return_value.close.assert_called_once()

    def test_cleanup_passed_stream(self, dummy_streams):
        """Context manager auto-closes streams passed as arguments"""
        raw, _ = dummy_streams
        with SeaStream(raw) as s:
            pass

        raw.close.assert_called_once()
