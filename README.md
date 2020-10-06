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
py steganography.py <-i input> [-c cover] [-o output]
```

## Examples
```
py src/steganography.py -i test/secret.txt -o normal.webp
py src/steganography.py --reveal -i normal.webp -o message.txt

py src/steganography.py -i test/redpill.webp -o normalred.webp
py src/steganography.py --reveal -i normalred.webp -o revealed.webp


py src/steganography.py -i test/secret.txt > hidden.webp

py src/steganography.py -i test/redpill.webp -c test/bluepill.webp > purple.webp

py src/steganography.py -i purple.webp --reveal > redpill.png

py src/steganography.py -i test/secret.txt -c test/redpill.webp -o red_with_msg.webp
```