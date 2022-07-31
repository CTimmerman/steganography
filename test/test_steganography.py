import logging
import logging.config
from io import BytesIO

import pytest
from PIL import Image
from steganography import hide, reveal


byts = b"The Matrix has you."


def test():
    cover = hide(byts, Image.new("RGB", (40, 20), color="white"))
    assert reveal(cover) == byts


def test_too_much_data():
    with pytest.raises(ValueError):
        hide(byts, Image.new("RGB", (4, 2)))


def test_fuzz():
    import random
    fuzz = 0
    for mode in ("1", "L", "LA", "RGB", "RGBA", "CMYK"):
        for i in range(10):
            fuzz += 1
            length = random.randint(0, 100)
            byts = bytes(random.randint(65, 90) for j in range(length))
            logging.info(f"Fuzz #{fuzz}: {length} bytes to mode {mode}.")
            try:
                cover = hide(byts, Image.new(mode, (100, 20), color="white"))
                assert reveal(cover) == byts
                for typ in ("PNG", "WEBP"):
                    if (typ == 'WEBP' and mode in ('1', 'L', 'LA', 'CMYK')
                            or typ == 'PNG' and mode in ('CMYK')):
                        continue  # WEBP saves 24 instead of 1 bpp.
                    with BytesIO() as fp:
                        try:
                            cover.save(fp, typ, lossless=True)
                            fp.flush()
                            fp.seek(0)
                            img = Image.open(fp)
                            try:
                                assert reveal(img) == byts
                                logging.info(f"Message okay in {mode} {typ}.")
                            except AssertionError:
                                logging.error(f"Message corrupted in {mode} {typ}. {cover.getbands()} cover bands => {img.getbands()} {typ} bands.")
                                cover.save(open(f'cover.{typ}', 'wb'), lossless=True)
                                img.save(open(f'img.{typ}', 'wb'), lossless=True)
                                raise
                        except OSError as e:
                            if "cannot write mode" in str(e):
                                logging.error(e)
                                raise
                            else:
                                logging.error(e)
                                raise
            except ValueError as e:
                logging.error(e)
                raise e


if __name__ == "__main__":
    # Don't create own logger as that's strongly advised against (So why offer it?!) according to https://docs.python.org/3/howto/logging.html
    # Use global setting and disable loggers of other modules instead. Also looks dirty!
    logging.basicConfig(level=logging.DEBUG)
    """
    All 3 snippets below leave PIL output like:
    DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
    DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 133
    """
    # for key in logging.Logger.manager.loggerDict.keys():
    #     if key != "__main__":
    #         logging.Logger.manager.loggerDict[key].disabled = True

    # logging.config.dictConfig({
    #     'version': 1,
    #     'disable_existing_loggers': True
    # })

    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for v in loggers:
        print("Existing logger", v, dir(v))
        v.disabled = True

    test_fuzz()
