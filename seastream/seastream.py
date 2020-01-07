"""

A stream that provides syntactic sugar around read/write operations on types.

"""
from typing import Any
from typing import Union
from typing import BinaryIO
from typing import SupportsBytes
from typing import ByteString
from typing import NoReturn

from os import PathLike
VALID_PATH_TYPES = (bytes, str, PathLike)
Pathish = Union[VALID_PATH_TYPES]


class SeaStream:
    """
    Wraps binary streams to ease read/write of types meeting requirements.

    It can wrap a passed stream or open a path passed to the constructor:
    >>> with SeaStream("filename") as s:
    >>>     s.write(supported_object)

    Using the stream as a context manager will make it close the wrapped
    stream when the context block exits.

    Reading types:
        >>> type_instance = stream.read(TypeName)

        Requires that the passed type:
          - implements from_bytes as a class method
          - has a _struct attribute with an integer size attribute

    Writing types:
        >>> stream.write(type_instance)

        To write type instances to stream, a class instance must implement the
        __bytes__ method that serializes the object to bytes.

    """

    def __init__(self, base: Union[BinaryIO, Pathish], mode: str = "rb"):
        """
        Build a seastream either by wrapping a passed stream or by opening a
        file specified as an argument.

        :param base: a path-like value or a stream-like object
        :param mode: None or a valid read mode for a stream
        """
        self._opened_stream = False

        if isinstance(base, VALID_PATH_TYPES):

            if not isinstance(mode, str):
                raise TypeError(
                    "mode must be a string specifying a binary file open mode"
                )

            if "b" not in mode:
                raise ValueError(
                    f"\"{mode}\" doesn't describe a binary file open mode")

            base = open(base, mode=mode)
            self._opened_stream = True

        self.wrapped_stream = base

    def write(self,
              obj: Union[ByteString, SupportsBytes]) -> None:
        """
        Write the passed object to the stream.

        If obj implements __bytes__, it is used to convert the object to a
        series of bytes, which are then written to the wrapped stream.

        Otherwise it is assumed to be bytes-like and an attempt is made to
        write it directly to the wrapped stream.

        :param obj: bytes-like object or a type
        :return: None
        """

        if hasattr(obj, "__bytes__"):  # can be converted to bytes
            return self.wrapped_stream.write(bytes(obj))

        else:  # assume it's bytes-like
            return self.wrapped_stream.write(obj)

    def read(self, arg: Any = -1) -> Union[bytes, Any, NoReturn]:
        """
        Read a supported type or read arg bytes from the wrapped stream.

        An error is raised if the arg is neither an int or a type.

        Types passed must have a from_bytes classmethod implemented.

        :param arg: an integer or a type
        :return: bytes or an instance of the passed type
        """

        if isinstance(arg, int):
            return self.wrapped_stream.read(arg)
        elif isinstance(arg, type):
            return arg.from_bytes(self.wrapped_stream.read(arg._struct.size))

        raise TypeError("Argument to read must be a type or an integer")

    def __enter__(self):
        """Make this a context manager"""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Make this a context manager, close wrapped stream"""
        self.wrapped_stream.close()
