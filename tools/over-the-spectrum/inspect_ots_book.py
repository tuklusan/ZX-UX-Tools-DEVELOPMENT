#!/usr/bin/env python3
"""Render a page or cropped page excerpt from the Over the Spectrum scan.

Usage:
  python inspect_ots_book.py path/to/book.pdf 73 path/to/excerpt.png --crop 25,225,400,410
Page numbers are 1-based PDF page numbers, not printed book numbers.
"""
import argparse
from pathlib import Path
import fitz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('pdf_page', type=int)
    parser.add_argument('png', type=Path)
    parser.add_argument('--crop', help='PDF-point rectangle: x0,y0,x1,y1')
    parser.add_argument('--scale', type=float, default=3.0)
    args = parser.parse_args()
    with fitz.open(args.pdf) as doc:
        page = doc[args.pdf_page - 1]
        clip = fitz.Rect(*map(float, args.crop.split(','))) if args.crop else None
        pix = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), clip=clip, alpha=False)
        args.png.parent.mkdir(parents=True, exist_ok=True)
        pix.save(args.png)


if __name__ == '__main__':
    main()
