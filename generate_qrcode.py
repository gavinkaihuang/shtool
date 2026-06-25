#!/usr/bin/env python3
import argparse
import os

import qrcode


def generate_qr(text: str, output_path: str | None = None) -> str:
    """Generate a QR code image from the given text."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path is None:
        safe_name = "".join(c if c.isalnum() else "_" for c in text)[:50]
        output_path = f"{safe_name}.png" if safe_name else "qrcode.png"

    img.save(output_path)
    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate a QR code image.")
    parser.add_argument("text", help="Text or URL to encode in the QR code.")
    parser.add_argument(
        "-o", "--output", help="Output image path (default: based on input text)."
    )
    args = parser.parse_args()

    output_path = generate_qr(args.text, args.output)
    print(f"QR code saved to: {output_path}")


if __name__ == "__main__":
    main()
