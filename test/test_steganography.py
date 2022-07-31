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


# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
supported_formats = {
	'BMP': ('1', 'L', 'RGB'),
	'DIB': ('1', 'L', 'RGB'),
	# 'EPS': ('L', 'RGB', 'CMYK'),  # Needs Ghostscript in path.
	'GIF': ('L', 'P'),
	'IM': ('1', 'L', 'LA', 'RGB', 'RGBA', 'CMYK'),
	# 'J2K': ('L', 'LA', 'RGB', 'RGBA'),
	'PCX': ('1', 'L', 'P', 'RGB'),
	'PNG': ('1', 'L', 'LA', 'I', 'P', 'RGB', 'RGBA'),
	'PPM': ('1', 'L', 'I', 'RGB'),
	# 'SGI': ('L', 'RGB', 'RGBA'),  # FIXME: PIL save closes file.
	'TGA': ('L', 'LA', 'P', 'RGB', 'RGBA'),
	'TIFF': ('1', 'L', 'LA', 'RGB', 'RGBA', 'CMYK'),
	'WEBP': ('RGB', 'RGBA'),  # WEBP saves 24 instead of 1 bpp.
}


def test_fuzz():
	import random
	for i in range(10):
		length = random.randint(0, 200)
		byts = bytes(random.randint(0, 255) for j in range(length))
		logging.info(f"Random message #{i}: {length} bytes: {byts}")
		for format in supported_formats:
			for mode in supported_formats[format]:
				try:
					# Test encoding.
					cover = hide(byts, Image.new(mode, (100, 20), color="white"))
					assert reveal(cover) == byts
					# Test format.
					with BytesIO() as fp:
						try:
							cover.save(fp, format, lossless=True)
							fp.flush()
							fp.seek(0)
							img = Image.open(fp)
							try:
								assert reveal(img) == byts
								logging.info(f"Message okay in {mode} {format}.")
							except AssertionError:
								logging.error(f"Message corrupted in {mode} {format}. {cover.getbands()} cover bands => {img.getbands()} {format} bands.")
								cover.save(open(f'cover.{format}', 'wb'), lossless=True)
								img.save(open(f'img.{format}', 'wb'), lossless=True)
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
