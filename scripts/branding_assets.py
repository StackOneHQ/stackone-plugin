"""Validate and collect the PNG branding assets this package distributes."""

from pathlib import PurePosixPath
import struct
import zlib

ICON_FIELDS = ("logo", "logoDark", "composerIcon", "composerIconDark")


def branding_files(interface, read_bytes):
    """Resolve plugin-root paths from a checkout or ZIP, rejecting invalid assets."""
    files = {}
    for field in ICON_FIELDS:
        reference = interface.get(field)
        if not isinstance(reference, str) or not reference.startswith("./"):
            raise ValueError(f"interface.{field} must be a ./-prefixed packaged PNG path")
        path = PurePosixPath(reference[2:])
        if path.is_absolute() or ".." in path.parts or "\\" in reference or path.suffix != ".png":
            raise ValueError(f"interface.{field} must point to a PNG inside the plugin root")
        name = path.as_posix()
        try:
            data = read_bytes(name)
        except (OSError, KeyError) as error:
            raise ValueError(f"interface.{field}: missing packaged asset {name}") from error
        if len(data) > 5 * 1024 * 1024:
            raise ValueError(f"interface.{field}: {name} exceeds 5 MiB")
        if len(data) < 45 or data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
            raise ValueError(f"interface.{field}: {name} is not a PNG with an IHDR header")
        width, height = struct.unpack(">II", data[16:24])
        if width != height or not 48 <= width <= 4096:
            raise ValueError(f"interface.{field}: {name} must be square and 48–4096 px")
        if zlib.crc32(data[12:29]) != struct.unpack(">I", data[29:33])[0]:
            raise ValueError(f"interface.{field}: {name} has an invalid PNG header checksum")
        if data[-12:] != b"\x00\x00\x00\x00IEND\xaeB`\x82":
            raise ValueError(f"interface.{field}: {name} is truncated")
        files[name] = data
    return files
