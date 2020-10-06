import pytest
from PIL import Image
from steganography import hide, reveal


def test():
    byts = b"The Matrix has you."
    cover = hide(byts, Image.new("RGB", (40, 20), color="white"))
    assert reveal(cover) == byts


def test_too_much_data():
    with pytest.raises(ValueError):
        hide(b"The Matrix has you.", Image.new("RGB", (4, 2)))
