# Steganography

## Installation

```
py -m venv .venv
```

GNU:
```
.venv/bin/activate
```

Windows:
```
.venv/Scripts/activate
```

```
pip install -r requirements.txt
```

Pillow >= 9.1.0 fails `pytest test\test_steganography.py` - https://github.com/python-pillow/Pillow/issues/6494


## Usage
```
py steganography.py [-i input] [--filler=zeroes|random] [-c cover] [-o output] [--reveal -r] [--verbose | -v] [--debug | -d] [--help | -h]
```
Default input is stdin.

Default cover is lossless white WebP.

Default output is stdout.

## Examples

In GNU, use `cat` and `/` instead of `type` and `\`. In Windows, use Command Prompt instead of PowerShell.
```
IO streams:

py src/steganography.py -i test/secret.txt > hidden.webp
or
type test\secret.txt | py src/steganography.py > hidden.webp

type hidden.webp | py src/steganography.py --reveal

File parameters:

py src/steganography.py -i test/secret.txt -o normal.webp
py src/steganography.py --reveal -i normal.webp -o message.txt

py src/steganography.py -i test/redpill.webp -o normalred.webp
py src/steganography.py --reveal -i normalred.webp -o revealed.webp

Cover image:

py src/steganography.py -i test/secret.txt -c test/redpill.webp -o red_with_msg.webp
py src/steganography.py --reveal -i red_with_msg.webp

py src/steganography.py -i test/redpill.webp -c test/bluepill.webp > purple.webp
py src/steganography.py -i purple.webp --reveal > secret.png
or
type purple.webp | py src/steganography.py --reveal > secret.webp

It would be a little more efficient to stop reading bits at the secret length, but right now you can use debug logging to check the filler bits:

py src/steganography.py -i test/redpill.webp -c test/bluepill.webp --filler=random > purple.webp
py src/steganography.py --reveal -i purple.webp --debug > purple_msg.webp

DEBUG:root:230,400 recovered bits: [0, 0, 1, 1, 1, 1, 1, 0]...[1, 1, 0, 0, 0, 0, 1, 1]
```
