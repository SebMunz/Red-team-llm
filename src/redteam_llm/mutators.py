from __future__ import annotations

import base64
import codecs


ZERO_WIDTH_SPACE = "\u200b"
HOMOGLYPHS = str.maketrans(
    {
        "a": "а",
        "e": "е",
        "i": "і",
        "o": "о",
        "p": "р",
        "c": "с",
        "x": "х",
    }
)


def to_base64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def to_hex(text: str) -> str:
    return text.encode("utf-8").hex()


def to_rot13(text: str) -> str:
    return codecs.encode(text, "rot_13")


def token_split(text: str) -> str:
    return " ".join(text)


def zero_width(text: str) -> str:
    return ZERO_WIDTH_SPACE.join(text)


def homoglyph(text: str) -> str:
    return text.translate(HOMOGLYPHS)


MUTATORS = {
    "base64": to_base64,
    "hex": to_hex,
    "rot13": to_rot13,
    "token-split": token_split,
    "zero-width": zero_width,
    "homoglyph": homoglyph,
}
