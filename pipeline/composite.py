"""Compose 4 panels into a 2x2 grid with folk-art-styled border, title, moral."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

# Folk-art palette (CLAUDE.md style references).
CREAM = (246, 234, 208)
INDIGO = (38, 52, 104)
TERRACOTTA = (178, 80, 55)
BLACK = (28, 24, 22)

PANEL_SIZE = 768
BORDER = 36
INNER_GUTTER = 12
TITLE_HEIGHT = 120
MORAL_HEIGHT = 110
OUTER_PADDING = 28

# Composite layout:
#   [ title               ]
#   [ 2x2 grid of panels  ]
#   [ moral line          ]

CANVAS_W = PANEL_SIZE * 2 + INNER_GUTTER + BORDER * 2 + OUTER_PADDING * 2
CANVAS_H = (
    PANEL_SIZE * 2
    + INNER_GUTTER
    + BORDER * 2
    + OUTER_PADDING * 2
    + TITLE_HEIGHT
    + MORAL_HEIGHT
)


def _load_font(size: int, bold: bool = False) -> Any:
    """Try a few common system fonts; fall back to default."""
    candidates_bold = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/NewYork.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ]
    candidates_regular = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/NewYork.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for path in candidates_bold if bold else candidates_regular:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    font: Any,
    fill: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = x0 + (x1 - x0 - tw) // 2 - bbox[0]
    ty = y0 + (y1 - y0 - th) // 2 - bbox[1]
    draw.text((tx, ty), text, font=font, fill=fill)


def _draw_dotted_border(
    draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int]
) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=color, width=4)
    # Decorative dotted inner line — a nod to Madhubani borders without going ornate.
    inset = 10
    dot_r = 3
    step = 20
    for x in range(x0 + inset, x1 - inset, step):
        draw.ellipse((x - dot_r, y0 + inset - dot_r, x + dot_r, y0 + inset + dot_r), fill=color)
        draw.ellipse((x - dot_r, y1 - inset - dot_r, x + dot_r, y1 - inset + dot_r), fill=color)
    for y in range(y0 + inset, y1 - inset, step):
        draw.ellipse((x0 + inset - dot_r, y - dot_r, x0 + inset + dot_r, y + dot_r), fill=color)
        draw.ellipse((x1 - inset - dot_r, y - dot_r, x1 - inset + dot_r, y + dot_r), fill=color)


def composite_panels(
    panel_paths: list[Path],
    title: str,
    moral_line: str,
    out_path: Path,
) -> Path:
    if len(panel_paths) != 4:
        raise ValueError(f"Expected 4 panels, got {len(panel_paths)}")

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), CREAM)
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(54, bold=True)
    moral_font = _load_font(30, bold=False)

    # Title band
    title_box = (OUTER_PADDING, OUTER_PADDING, CANVAS_W - OUTER_PADDING, OUTER_PADDING + TITLE_HEIGHT)
    _draw_text_centered(draw, title, title_box, title_font, INDIGO)

    # Grid area
    grid_x0 = OUTER_PADDING
    grid_y0 = OUTER_PADDING + TITLE_HEIGHT
    grid_x1 = CANVAS_W - OUTER_PADDING
    grid_y1 = grid_y0 + PANEL_SIZE * 2 + INNER_GUTTER + BORDER * 2

    _draw_dotted_border(draw, (grid_x0, grid_y0, grid_x1, grid_y1), INDIGO)

    # Paste panels in 2x2 layout inside the border.
    inner_x0 = grid_x0 + BORDER
    inner_y0 = grid_y0 + BORDER
    positions = [
        (inner_x0, inner_y0),
        (inner_x0 + PANEL_SIZE + INNER_GUTTER, inner_y0),
        (inner_x0, inner_y0 + PANEL_SIZE + INNER_GUTTER),
        (inner_x0 + PANEL_SIZE + INNER_GUTTER, inner_y0 + PANEL_SIZE + INNER_GUTTER),
    ]
    for path, (px, py) in zip(panel_paths, positions, strict=True):
        panel = Image.open(path).convert("RGB").resize(
            (PANEL_SIZE, PANEL_SIZE), Image.Resampling.LANCZOS
        )
        canvas.paste(panel, (px, py))

    # Moral band
    moral_box = (
        OUTER_PADDING,
        grid_y1,
        CANVAS_W - OUTER_PADDING,
        grid_y1 + MORAL_HEIGHT,
    )
    _draw_text_centered(draw, moral_line, moral_box, moral_font, TERRACOTTA)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, format="PNG", optimize=True)
    return out_path
