"""Steganography

2020-10-07 v1.0 by Cees Timmerman.
2022-07-31 v1.0.1 Don't break on 1 bpp PNG.
"""
import logging
import math
from secrets import randbits

from PIL import Image  # pip install Pillow

DEBUG_CONTEXT = 8
# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
SUPPORTED_FORMATS = {
	'BMP': ('1', 'L', 'RGB'),
	'DIB': ('1', 'L', 'RGB'),
	# 'EPS': ('L', 'RGB', 'CMYK'),  # Needs Ghostscript in path.
	'GIF': ('L', 'P'),
	'IM': ('1', 'L', 'LA', 'RGB', 'RGBA', 'CMYK'),
	# 'J2K': ('L', 'LA', 'RGB', 'RGBA'),
	'PCX': ('1', 'L', 'P', 'RGB'),
	'PNG': ('1', 'L', 'LA', 'I', 'P', 'RGB', 'RGBA'),
	'PPM': ('1', 'L', 'I', 'RGB'),
	# 'SGI': ('L', 'RGB', 'RGBA'),  # FIXME: PIL save() closes file.
	'TGA': ('L', 'LA', 'P', 'RGB', 'RGBA'),
	'TIFF': ('1', 'L', 'LA', 'RGB', 'RGBA', 'CMYK'),
	'WEBP': ('RGB', 'RGBA'),  # WEBP saves 24 instead of 1 bpp.
}


class BraceMessage:
	"""Struct for lazy formatting."""

	def __init__(self, fmt, /, *args, **kwargs):
		self.fmt = fmt
		self.args = args
		self.kwargs = kwargs

	def __str__(self):
		return self.fmt.format(*self.args, **self.kwargs)


lf = BraceMessage


def bits2bytes(bits):
	while True:
		byte = 0
		for _ in range(8):
			try:
				byte = (byte << 1) | next(bits)
			except StopIteration:
				return
		yield byte


def bytes2bits(byts):
	for byte in byts:
		for bit in format(byte, "08b"):
			yield int(bit)


def get_lowest_bits(img):
	band_count = len(img.getbands())
	for pixel in img.getdata():
		if band_count == 1:
			pixel = [pixel]
		for i in range(band_count):
			yield pixel[i] & 1


def zeroes():
	while True:
		yield 0


def random_bits():
	while True:
		yield randbits(1)


def rand(seed=123456789):
	"""https://stackoverflow.com/a/3062783/819417"""
	seed = (1103515245 * seed + 12345) % 2 ** 31
	return seed


def set_lowest_bits(img, bits=None, filler=None):
	if bits is None:
		bits = []

	logging.debug("Setting bits: %s...", bits[:DEBUG_CONTEXT])
	bits = iter(bits)

	w, h = img.size
	mode = img.getbands()
	logging.debug("Bands: %s", mode)
	band_range = range(len(mode))
	mode = mode[0]
	pixels = img.load()

	done = False
	for y in range(h):
		for x in range(w):
			pixel = pixels[x, y]
			if isinstance(pixel, int):
				pixel = [pixel]
			else:
				pixel = list(pixel)
			for i in band_range:
				try:
					bit = next(bits)
					if bit:
						pixel[i] |= 1
					else:
						pixel[i] &= ~1

				except StopIteration:
					if filler:
						bits = filler()
					else:
						done = True
						break
			if y < 1 and x < 3:
				logging.debug(
					"Setting %s at %s, %s to %s...",
					pixels[x, y], x, y, pixel
				)

			if mode == '1':
				pixels[x, y] = 1 if pixel[0] == 255 else 0
			elif mode == 'I':
				pixels[x, y] = pixel[0]
			else:
				pixels[x, y] = tuple(pixel)
			if done:
				return img

	return img


def hide(data, cover=None, filler=None):
	data_length = len(data)
	cover_mode = "RGB"
	if not cover:
		logging.info("Generating 4:3 image to hold data...")
		w = 0
		h = 0
		while True:
			w += 4
			h += 3
			max_bytes = w * h * len(cover_mode) // 8
			if max_bytes > data_length + math.ceil(math.log2(max_bytes)):
				break
		logging.info("%ix%i", w, h)
		cover = Image.new(cover_mode, (w, h), color=(255, 255, 255, 0))

	max_bits = cover.size[0] * cover.size[1] * len(cover.mode)
	header_size = math.ceil(math.log2(max_bits // 8))
	max_bits -= header_size
	max_bytes = max_bits // 8

	logging.info(
		lf("Cover has {:,} bits / {:,} bytes available. ({}-bit header)", max_bits, max_bytes, header_size)
	)

	logging.info(
		lf("Message has {:,} bits / {:,} bytes: {}... {}", data_length * 8, data_length, data[:DEBUG_CONTEXT], [c for c in data[:DEBUG_CONTEXT]])
	)

	if data_length * 8 > max_bits:
		raise ValueError(f"Message too long for cover. {data_length*8:,} > {max_bits:,} bits.")

	if data_length > (2 ** header_size):
		raise ValueError(f"Message too long for header. {data_length:,} >= {2**header_size:,} bytes.")

	bit_stream = bytes2bits(data)
	bits = list(bit_stream)
	# logging.debug(lf("{} data bits: {}...", len(bits), bits[:100]))

	length_header = [int(b) for b in format(data_length, f"0{header_size}b")]
	# logging.debug(lf("Add {}-bit header to specify length of data. {}", header_size, length_header))
	bits = length_header + bits

	cover = set_lowest_bits(cover, bits, filler)
	logging.info("Data hidden.")
	return cover


def reveal(cover):
	max_bits = cover.size[0] * cover.size[1] * len(cover.mode)
	header_size = math.ceil(math.log2(max_bits // 8))

	bits = list(get_lowest_bits(cover))
	logging.debug(lf("{:,} recovered bits: {}...{}", len(bits), bits[:DEBUG_CONTEXT], bits[-DEBUG_CONTEXT:]))

	data_length_bits = bits[:header_size]
	data_length_string = "".join(str(b) for b in data_length_bits)
	# logging.debug(lf("{header_size}-bit header: {data_length_string} ({int(data_length_string, 2):,})"))

	data_length = int(data_length_string, 2)
	logging.debug(lf("Data length: {:,}", data_length))

	data = list(bits2bytes(iter(bits[header_size:header_size + data_length * 8])))
	logging.debug(
		lf("{:,} recovered bytes: {}... {}...", len(data), data[:DEBUG_CONTEXT], bytes(data[:DEBUG_CONTEXT]))
	)
	return bytes(data)


if __name__ == "__main__":
	import io, os, sys
	'''
	from PIL import ImageDraw, ImageFont
	base = Image.new("RGBA", (320, 240), color="black")
	overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
	text = "Red pill"
	font = ImageFont.truetype("arial.ttf", 50)
	draw = ImageDraw.Draw(overlay)
	text_w, text_h = draw.textsize(text, font=font)
	draw.text(
		(base.size[0] / 2 - text_w / 2, base.size[1] / 2 - text_h / 2),
		"Red pill",
		font=font,
		fill=(255, 0, 0, 200),
	)
	out = Image.alpha_composite(base, overlay)
	out.save("test/redpill.webp", lossless=True)
	sys.exit(0)
	'''
	args = sys.argv[1:]
	try:
		if "--debug" in args or "-d" in args:
			logging.basicConfig(level=logging.DEBUG)
		elif "--verbose" in args or "-v" in args:
			logging.basicConfig(level=logging.INFO)
		else:
			logging.basicConfig(level=logging.WARNING)

		if "--help" in args or "-h" in args:
			raise IndexError

		data_file = None if "-i" not in args else args[args.index("-i") + 1]
		filler_fun = (
			zeroes
			if "--filler=zeroes" in args
			else random_bits
			if "--filler=random" in args
			else None
		)
		cover_file = None if "-c" not in args else args[args.index("-c") + 1]
		output_file = None if "-o" not in args else args[args.index("-o") + 1]
	except IndexError:
		print(
			"Usage: [-i input] [--filler=zeroes|random] [-c cover] [-o output] [--reveal -r] [--verbose | -v] [--debug | -d] [--help | -h]",
			file=sys.stderr,
		)
		sys.exit(1)

	if "--test" in args:  # Should be ran from project root.
		import pytest
		sys.exit(pytest.main(sys.argv[2:]))

	if "--reveal" in args or "-r" in args:
		if data_file:
			secret = reveal(Image.open(data_file))
		else:
			fp = io.BytesIO()
			fp.write(sys.stdin.buffer.read())
			secret = reveal(Image.open(fp))
		if output_file:
			open(output_file, "wb").write(secret)
		else:
			os.write(1, secret)
	else:
		try:
			if data_file:
				secret = open(data_file, "rb").read()
			else:
				secret = sys.stdin.buffer.read()

			image = hide(
				secret, None if not cover_file else Image.open(cover_file), filler_fun
			)
		except ValueError as e:
			print(e, file=sys.stderr)
			sys.exit(2)

		if output_file:
			image.save(output_file, lossless=True)
		else:
			# Write data to stdout for redirection.
			out = io.BytesIO()
			image.save(out, format="WEBP", lossless=True)
			out.seek(0)
			os.write(1, out.read())
