import base64 as b64
import binascii
from collections.abc import Callable
from urllib.parse import (
    quote,
    quote_plus,
    unquote,
    unquote_plus,
)
from constants import EncodingFormat, BASE64SAFE_CHARSET


type EncoderFn = Callable[[bytes], str]
type DecoderFn = Callable[[str], bytes]


def encode_base64(data: bytes) -> str:
    return b64.b64encode(data).decode("ascii")


def decode_base64(data: str) -> bytes:
    cleaned = "".join(data.split())
    return b64.b64decode(cleaned, validate=True)


def encode_base64url(data: bytes) -> str:
    return b64.urlsafe_b64encode(data).decode("ascii")


def decode_base64url(data: str) -> bytes:
    cleaned = "".join(data.split())
    return b64.urlsafe_b64decode(cleaned)


def encode_base64safe(data: bytes) -> str:
    """URL-safe Base64 without padding (RFC 4648 sec 5, no '=')."""
    return b64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def decode_base64safe(data: str) -> bytes:
    """Decode unpadded URL-safe Base64; re-adds padding automatically."""
    cleaned = "".join(data.split())
    # Re-add missing '=' padding so urlsafe_b64decode accepts it
    padding = (4 - len(cleaned) % 4) % 4
    return b64.urlsafe_b64decode(cleaned + "=" * padding)


def encode_base32(data: bytes) -> str:
    return b64.b32encode(data).decode("ascii")


def decode_base32(data: str) -> bytes:
    cleaned = "".join(data.split()).upper()
    return b64.b32decode(cleaned)


def encode_hex(data: bytes) -> str:
    return data.hex()


def decode_hex(data: str) -> bytes:
    cleaned = data.strip()
    for sep in (" ", ":", "-", "."):
        cleaned = cleaned.replace(sep, "")
    return bytes.fromhex(cleaned)


def encode_url(data: bytes, *, form: bool = False) -> str:
    text = data.decode("utf-8")
    if form:
        return quote_plus(text)
    return quote(text, safe="")


def decode_url(data: str, *, form: bool = False) -> bytes:
    if form:
        return unquote_plus(data).encode("utf-8")
    return unquote(data).encode("utf-8")


ENCODER_REGISTRY: dict[
    EncodingFormat,
    tuple[EncoderFn, DecoderFn],
] = {
    EncodingFormat.BASE64: (encode_base64, decode_base64),
    EncodingFormat.BASE64URL: (encode_base64url, decode_base64url),
    EncodingFormat.BASE64SAFE: (encode_base64safe, decode_base64safe),
    EncodingFormat.BASE32: (encode_base32, decode_base32),
    EncodingFormat.HEX: (encode_hex, decode_hex),
    EncodingFormat.URL: (
        lambda data: encode_url(data),
        lambda data: decode_url(data),
    ),
}


def encode(data: bytes, fmt: EncodingFormat) -> str:
    encoder_fn, _ = ENCODER_REGISTRY[fmt]
    return encoder_fn(data)


def decode(data: str, fmt: EncodingFormat) -> bytes:
    _, decoder_fn = ENCODER_REGISTRY[fmt]
    return decoder_fn(data)


def try_decode(data: str, fmt: EncodingFormat) -> bytes | None:
    try:
        return decode(data, fmt)
    except (
        ValueError,
        binascii.Error,
        UnicodeDecodeError,
        UnicodeEncodeError,
    ):
        return None