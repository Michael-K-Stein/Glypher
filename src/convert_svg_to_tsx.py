import os
import re

from pyprinter.printer import print_info, print_log, print_success


class SvgConvertionException(Exception):
    pass


class TsxSvgData:
    svg_file_path = ""
    svg_dirty_data = ""
    svg_data = ""
    tsx_file_path = ""
    tsx_file_name = ""
    glyph_name = ""
    glyph_custom_css_class = ""
    tsx_file_content = ""


def _convert_svg_data_to_tsx_data(svg_input_data: TsxSvgData) -> TsxSvgData:
    svg_dirty_data = svg_input_data.svg_dirty_data
    reg = re.search(
        r"(?P<svg_data>(\<svg\s+.*?\>.*?\<\/svg\>))",
        svg_dirty_data,
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    if not reg:
        raise SvgConvertionException(f"Failed to extract svg data!")

    svg_data = reg.group("svg_data")
    svg_data = re.sub(
        r'\s+width="\d+"\s+height="\d+"',
        r' className="min-h-full min-w-full max-h-full max-w-full w-full h-full"',
        svg_data,
        re.MULTILINE,
    )
    svg_data = re.sub(
        r"(\<svg\s+.*?\>)",
        r'\1<rect fill="transparent" stroke="none" width="100%" height="100%" />',
        svg_data,
        re.MULTILINE,
    )

    svg_data = re.sub(
        r"(\w+)-(\w)(\w+)=",
        lambda m: f"{m.group(1)}{m.group(2).upper()}{m.group(3)}=",
        svg_data,
    )

    c = svg_dirty_data.count(" fill=")
    c -= svg_dirty_data.count(' fill="none"')
    c -= svg_dirty_data.count(" fill='none'")
    c -= svg_dirty_data.count(' fill="#FFFFFF"')
    if c > 1:
        print_info(f"Multiple fills! {c}")
    else:
        svg_data = re.sub(r'\bfill="#\w+?"', r'fill="currentColor"', svg_data)
        svg_data = re.sub(r'\bstroke="#\w+?"', r'stroke="currentColor"', svg_data)

    output_data = svg_input_data

    output_data.svg_dirty_data = svg_dirty_data
    output_data.svg_data = svg_data
    tsx_name = os.path.splitext(os.path.basename(svg_input_data.svg_file_path))[
        0
    ].replace("_", "-")
    output_data.glyph_custom_css_class = f"{tsx_name}-glyph"
    output_data.tsx_file_name = tsx_name + ".tsx"
    output_data.glyph_name = (
        "".join((x[0].upper() + x[1:]) for x in tsx_name.split("-")) + "Glyph"
    )
    output_data.tsx_file_content = f'import "./glyphs.css"\nimport {{ Tooltip, TooltipProps }} from "@mui/material";\nimport Glypher from "./glypher"\nexport default function {output_data.glyph_name}({{glyphTitle, placement, ...props}} : {{glyphTitle: string, placement?: TooltipProps[ "placement" ]}} & React.HTMLAttributes<HTMLDivElement>){{return(<Glypher glyphTitle={{glyphTitle}} placement={{placement}} {{ ...props }}><div className="svg-glyph {output_data.glyph_custom_css_class}">{output_data.svg_data}</div></Glypher>);}};'

    return output_data


def convert_svg_to_tsx(svg_file_path: str) -> TsxSvgData:
    with open(svg_file_path, "r") as f:
        # Contains redundant headers
        svg_dirty_data = f.read()

    input_data = TsxSvgData()
    input_data.svg_dirty_data = svg_dirty_data
    input_data.svg_file_path = svg_file_path

    try:
        output_data = _convert_svg_data_to_tsx_data(input_data)
    except Exception as ex:
        raise SvgConvertionException(str(ex))

    print_success(f"Extracted SVG to TSX {output_data.glyph_name}")

    return output_data


def convert_svg_file_to_tsx_file(svg_file_path: str, output_dir: str) -> None:
    tsx_data = convert_svg_to_tsx(svg_file_path)

    tsx_data.tsx_file_path = os.path.join(output_dir, tsx_data.tsx_file_name)

    with open(tsx_data.tsx_file_path, "w") as f:
        f.write(tsx_data.tsx_file_content)
    print_log(f"{tsx_data.glyph_name} created as {tsx_data.tsx_file_path}")
