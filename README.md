# Steganography

## Installation
```
py -m venv .venv
```
GNU: `.venv/bin/activate`

Windows: `.venv/Scripts/activate`

```
pip install -r requirements.txt
```


## Usage
```
py steganography.py <-i input> [-c cover] [-o output] [--reveal]
```

## Examples
```
TODO: Stream input.

Text streams:
py src/steganography.py -i test/secret.txt > hidden.webp
py src/steganography.py --reveal -i hidden.webp

Text files:
py src/steganography.py -i test/secret.txt -o normal.webp
py src/steganography.py --reveal -i normal.webp -o message.txt

Binary files:
py src/steganography.py -i test/redpill.webp -o normalred.webp
py src/steganography.py --reveal -i normalred.webp -o revealed.webp

Text file in cover image:
py src/steganography.py -i test/secret.txt -c test/redpill.webp -o red_with_msg.webp
py src/steganography.py --reveal -i red_with_msg.webp

Binary file in cover image:
py src/steganography.py -i test/redpill.webp -c test/bluepill.webp > purple.webp
py src/steganography.py -i purple.webp --reveal > redpill.png
```
