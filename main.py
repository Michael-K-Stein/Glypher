"""
Purpose: Create TSX components from SVG files
Author: Michael K. Steinberg
Created: 23/04/2024
Name: main.py
"""

import os
from argparse import ArgumentParser
import re

from pyprinter.printer import print_error, print_log
from src.convert_svg_to_tsx import SvgConvertionException, convert_svg_file_to_tsx_file
from pyprinter.walker import validate_file_path, validate_file_path_dir, walk_files


def convert_files(input_path: str, output_dir: str) -> None:
    # Sanity for inputs
    if not os.path.exists(input_path):
        raise IOError(f"{input_path} does not exist!")

    if not os.path.exists(output_dir):
        raise IOError(f"Output directory does not exist!")

    if not os.path.isdir(output_dir):
        raise IOError(f"Output path must be a directory!")

    if not os.path.isdir(input_path):
        convert_svg_file_to_tsx_file(input_path, output_dir)
        return

    def callback(_file_dir, file_path):
        print_log(f"Handling file {file_path}")
        convert_svg_file_to_tsx_file(file_path, output_dir)

    walk_files(input_path, callback, re.compile(r".*\.svg$", re.IGNORECASE))


def main():
    parser = ArgumentParser(description="Convert SVG files to TSX glyphs.")
    parser.add_argument(
        "input_path",
        type=validate_file_path,
        help="Path to an SVG file or a directory of SVG files",
    )
    parser.add_argument(
        "output_path",
        type=validate_file_path_dir,
        help="Path to save the converted TSX files",
    )

    args = parser.parse_args()

    print_log(f"Input: {args.input_path}")
    print_log(f"Output: {args.output_path}")

    try:
        convert_files(args.input_path, args.output_path)
    except SvgConvertionException as ex:
        print_error(f"Conversion failed: {str(ex)}")


if __name__ == "__main__":
    main()
