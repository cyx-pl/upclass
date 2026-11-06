"""Bundled OFL fonts supporting Polish characters in generated documents."""

from functools import lru_cache
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@lru_cache(maxsize=1)
def register_pdf_fonts():
    directory = Path(__file__).with_name("fonts")
    for name in ("NotoSans", "NotoSans-Bold", "NotoSans-Italic", "NotoSans-BoldItalic"):
        pdfmetrics.registerFont(TTFont(name, str(directory / f"{name}.ttf")))
    pdfmetrics.registerFontFamily(
        "NotoSans",
        normal="NotoSans",
        bold="NotoSans-Bold",
        italic="NotoSans-Italic",
        boldItalic="NotoSans-BoldItalic",
    )
