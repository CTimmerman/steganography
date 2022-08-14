from io import BytesIO
import logging
import logging.config
import random

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import pytest
from PIL import Image

from steganography import hide, reveal, SUPPORTED_FORMATS

data = b"The Matrix has you."


def test():
	cover = hide(data, Image.new("RGB", (40, 20), color="white"))
	assert reveal(cover) == data  # nosec


def test_too_much_data():
	with pytest.raises(ValueError):
		hide(data, Image.new("RGB", (4, 2)))


def test_fuzz():
	for i in range(10):
		length = random.randint(0, 200)  # nosec
		random_bytes = bytes(random.randint(0, 255) for j in range(length))  # nosec
		logging.info(f"Random message #{i}: {length} bytes: {random_bytes}")
		for ext, modes in SUPPORTED_FORMATS.items():
			for mode in modes:
				try:
					logging.info(f"Testing {mode} {ext}...")
					cover = hide(random_bytes, Image.new(mode, (100, 20), color="white"))
					assert reveal(cover) == random_bytes  # nosec
					with BytesIO() as fp:
						try:
							cover.save(fp, ext, lossless=True)
							fp.flush()
							fp.seek(0)
							img = Image.open(fp)
							try:
								assert reveal(img) == random_bytes  # nosec
								logging.info(f"Message okay in {mode} {ext}.")
							except AssertionError:
								logging.error(f"Message corrupted in {mode} {ext}. {cover.getbands()} cover bands => {img.getbands()} {ext} bands.")
								cover.save(open(f'cover.{ext}', 'wb'), lossless=True)
								img.save(open(f'img.{ext}', 'wb'), lossless=True)
								raise
						except OSError as e:
							logging.error(e)
							raise
				except ValueError as e:
					logging.error(e)
					raise e


if __name__ == "__main__":
	# Don't create own logger as that's strongly advised against (So why offer it?!) according to https://docs.python.org/3/howto/logging.html
	# Use global setting and disable loggers of other modules instead. Also looks dirty!
	logging.basicConfig(level=logging.DEBUG)
	loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]  # pylint: disable=no-member
	for v in loggers:
		print("Existing logger", v)
		v.setLevel('WARNING')

	#test_fuzz()
	pytest.main(['--log-cli-level', 'WARNING'])
