#!/usr/bin/env python3
import math
import random
import sys

from PySide6.QtCore import QRect, Qt, QStandardPaths, QTimer, QUrl, Signal
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}

# --- Themes ---
THEMES = {
    "arcade": {
        "bg": "#0e0b16", "panel": "#131022", "panel2": "#171529",
        "text": "#e8e4ff", "border": "#6d5bd0", "dim": "#2c2840",
        "hint": "#7b76a6", "tape": "#29f1ff",
        "green": "#3dff3d", "cyan": "#29f1ff", "magenta": "#ff4fd8",
        "yellow": "#ffd23f", "red": "#ff4444", "led_bg": "#04030a",
        "reel_body": "#3ddc84", "reel_rim": "#0a2818",
        "reel_hub": "#14121f", "reel_bg": "#05040b",
        "selected_bg": "#ff4fd8", "selected_text": "#0e0b16",
        "deck_border": "#3d3a55",
        "button_bg": "#262138", "button_border": "#8a7dff",
        "button_hover_bg": "#332a4d", "button_pressed_bg": "#0e0b16",
        "play_bg": "#8f1d3c", "play_border": "#ff4fd8",
        "play_hover": "#b0254a", "play_pressed": "#3d0b19",
    },
    "ubuntu": {
        "bg": "#2c001e", "panel": "#3d1f38", "panel2": "#2a1628",
        "text": "#f2e9ee", "border": "#e95420", "dim": "#5e2750",
        "hint": "#c9a8bf", "tape": "#8fcee9",
        "green": "#e95420", "cyan": "#8fcee9", "magenta": "#ff9c78",
        "yellow": "#f6c445", "red": "#c0392b", "led_bg": "#12000c",
        "reel_body": "#7a8590", "reel_rim": "#3a424c",
        "reel_hub": "#2a1628", "reel_bg": "#120a10",
        "selected_bg": "#e95420", "selected_text": "#2c001e",
        "deck_border": "#5e2750",
        "button_bg": "#40282f", "button_border": "#a86440",
        "button_hover_bg": "#52323c", "button_pressed_bg": "#1c0f14",
        "play_bg": "#e95420", "play_border": "#ffb08a",
        "play_hover": "#ff5c24", "play_pressed": "#7a2c10",
    },
    "phosphor": {
        "bg": "#000803", "panel": "#03130a", "panel2": "#02100a",
        "text": "#b8ffe0", "border": "#1f7050", "dim": "#0e3a28",
        "hint": "#5f9e80", "tape": "#8dffb2",
        "green": "#3dff7a", "cyan": "#8dffb2", "magenta": "#7dffd0",
        "yellow": "#ffe87a", "red": "#ffb42b", "led_bg": "#000b05",
        "reel_body": "#2a7a4a", "reel_rim": "#123b24",
        "reel_hub": "#02100a", "reel_bg": "#01100a",
        "selected_bg": "#0f5c33", "selected_text": "#04140a",
        "deck_border": "#0e3a28",
        "button_bg": "#062b18", "button_border": "#1f7050",
        "button_hover_bg": "#0a4024", "button_pressed_bg": "#020c07",
        "play_bg": "#0f5c33", "play_border": "#6affa0",
        "play_hover": "#14804a", "play_pressed": "#053018",
    },
    "bios": {
        "bg": "#05051a", "panel": "#0a0f33", "panel2": "#060a24",
        "text": "#d8dce8", "border": "#6f8cff", "dim": "#2c3a70",
        "hint": "#8fa0c8", "tape": "#7fd4ff",
        "green": "#e8e8ee", "cyan": "#7fd4ff", "magenta": "#b9a8ff",
        "yellow": "#ffff8a", "red": "#ff8a7a", "led_bg": "#00000c",
        "reel_body": "#4a5a8a", "reel_rim": "#222c52",
        "reel_hub": "#060a24", "reel_bg": "#04071a",
        "selected_bg": "#0f2060", "selected_text": "#ffffff",
        "deck_border": "#2c3a70",
        "button_bg": "#0a1140", "button_border": "#6f8cff",
        "button_hover_bg": "#111c66", "button_pressed_bg": "#040a20",
        "play_bg": "#0f2060", "play_border": "#9ab0ff",
        "play_hover": "#1a2f7a", "play_pressed": "#060d33",
    },
}
THEME_ORDER = list(THEMES)

# Wird von apply_theme() gesetzt; Paint-Code liest diese Konstanten zur Laufzeit.
EDGE = QColor("#6d5bd0")
NEON_GREEN = QColor("#3dff3d")
NEON_CYAN = QColor("#29f1ff")
NEON_MAGENTA = QColor("#ff4fd8")
NEON_YELLOW = QColor("#ffd23f")
GRID_DIM = QColor("#2c2840")
EQ_RED = QColor("#ff4444")
LED_BG = QColor("#04030a")
REEL_BODY = QColor("#3ddc84")
REEL_RIM = QColor("#0a2818")
REEL_HUB = QColor("#14121f")
REEL_BG = QColor("#05040b")
STYLESHEET = ""


def build_stylesheet(c):
    return f"""
QWidget {{
    background: {c['bg']};
    color: {c['text']};
    font-family: "DejaVu Sans Mono", monospace;
    font-weight: bold;
    font-size: 12px;
}}
QListWidget {{
    background: {c['panel']};
    border: 3px solid {c['border']};
    border-radius: 0;
    padding: 4px;
    color: {c['text']};
}}
QListWidget::item {{
    padding: 4px 8px;
    border: 1px solid {c['dim']};
    background: {c['panel2']};
}}
QListWidget::item:selected {{
    background: {c['selected_bg']};
    color: {c['selected_text']};
}}
QFrame#boombox {{
    background: {c['panel']};
    border: 3px solid {c['border']};
    border-radius: 0;
}}
QFrame#center {{ background: transparent; border: none; }}
QFrame#deck {{
    background: {c['bg']};
    border: 3px solid {c['deck_border']};
    border-radius: 0;
}}
QLabel#hint {{
    color: {c['hint']};
    font-size: 11px;
    letter-spacing: 2px;
}}
QLabel#tape {{
    color: {c['tape']};
    font-size: 12px;
    letter-spacing: 2px;
    background: transparent;
}}
QLabel#knoblabel {{
    color: {c['yellow']};
    font-size: 11px;
    letter-spacing: 2px;
    background: transparent;
}}
QPushButton {{
    background: {c['button_bg']};
    border: 3px solid {c['button_border']};
    border-radius: 0;
    padding: 6px 8px;
    color: {c['text']};
    font-weight: bold;
    font-size: 12px;
}}
QPushButton:hover {{
    background: {c['button_hover_bg']};
    border-color: {c['tape']};
}}
QPushButton:pressed {{
    background: {c['button_pressed_bg']};
    border-color: {c['magenta']};
    padding: 7px 7px 5px 9px;
}}
QPushButton#play {{
    background: {c['play_bg']};
    border-color: {c['play_border']};
    color: #ffffff;
}}
QPushButton#play:hover {{ background: {c['play_hover']}; }}
QPushButton#play:pressed {{ background: {c['play_pressed']}; }}
"""


def apply_theme(name):
    global EDGE, NEON_GREEN, NEON_CYAN, NEON_MAGENTA, NEON_YELLOW, GRID_DIM
    global EQ_RED, LED_BG, REEL_BODY, REEL_RIM, REEL_HUB, REEL_BG, STYLESHEET
    c = THEMES[name]
    EDGE = QColor(c["border"])
    NEON_GREEN = QColor(c["green"])
    NEON_CYAN = QColor(c["cyan"])
    NEON_MAGENTA = QColor(c["magenta"])
    NEON_YELLOW = QColor(c["yellow"])
    GRID_DIM = QColor(c["dim"])
    EQ_RED = QColor(c["red"])
    LED_BG = QColor(c["led_bg"])
    REEL_BODY = QColor(c["reel_body"])
    REEL_RIM = QColor(c["reel_rim"])
    REEL_HUB = QColor(c["reel_hub"])
    REEL_BG = QColor(c["reel_bg"])
    STYLESHEET = build_stylesheet(c)


apply_theme("arcade")

# 5x7 Bitmap-Font: jedes '#' wird als Quadrat gezeichnet -> immer knackig,
# unabhaengig von DPI/Skalierung.
GLYPHS = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ".": (".....", ".....", ".....", ".....", ".....", "..##.", "..##."),
    ",": (".....", ".....", ".....", ".....", "..##.", "..##.", "..#.."),
    ":": (".....", "..##.", "..##.", ".....", "..##.", "..##.", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "\\": ("#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".##..", "#.#.#", "#..#.", ".##.#"),
    "(": ("..#..", ".#...", "#....", "#....", "#....", ".#...", "..#.."),
    ")": ("..#..", "...#.", "....#", "....#", "....#", "...#.", "..#.."),
    "[": ("..###", "..#..", "..#..", "..#..", "..#..", "..#..", "..###"),
    "]": ("###..", "..#..", "..#..", "..#..", "..#..", "..#..", "###.."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "#": (".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", "....."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
}

_ASCII_MAP = str.maketrans({"Ä": "A", "Ö": "O", "Ü": "U", "ß": "S", "ä": "A", "ö": "O", "ü": "U"})


def pxfill(painter, x, y, w, h, color):
    """Robustes Pixel-Rechteck: explizites QRect+QBrush, unabhaengig vom
    aktuellen Painter-Brush (PySide6-Workaround)."""
    painter.fillRect(QRect(int(x), int(y), int(w), int(h)), QBrush(QColor(color)))


def is_audio(url):
    return any(url.toLocalFile().lower().endswith(ext) for ext in AUDIO_EXTENSIONS)


def bit_text_width(text, scale):
    return max(0, (len(text) * 6 - 1) * scale)


def draw_bit_text(painter, text, x, y, color, scale):
    """Bitmap-Font zeichnen: pro Pixel ein Quadrat -> nie verwaschen."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)
    cx = x
    for ch in text.upper().translate(_ASCII_MAP):
        pattern = GLYPHS.get(ch, GLYPHS.get("?"))
        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "#":
                    pxfill(painter, cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale



def pixel_block_disc(painter, cx, cy, outer, inner, body, hole):
    """Blockige Pixelscheibe gefuellt mit Ringen."""
    for dy in range(-outer, outer + 1):
        for dx in range(-outer, outer + 1):
            d2 = dx * dx + dy * dy
            if d2 <= outer * outer:
                c = body
                if d2 <= inner * inner:
                    c = hole
                pxfill(painter, cx + dx, cy + dy, 1, 1, c)


def pixel_line(painter, x0, y0, x1, y1, color, step=2, size=2):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) / step)
    if steps <= 0:
        steps = 1
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        pxfill(painter, x, y, size, size, color)


class LedDisplay(QWidget):
    """Pixel-LED-Screen mit Equalizer, Marquee und Zeit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "INSERT TAPE "
        self.elapsed = 0
        self.total = 0
        self.playing = False
        self.volume = 50
        self.bars = [0.0] * 14
        self._tick = 0
        self.setFixedHeight(210)
        worst = bit_text_width("PLAY  VOL 100  STEREO", 3)
        self.setMinimumWidth(worst + 28)
        tm = QTimer(self)
        tm.timeout.connect(self._animate)
        tm.start(60)

    def set_info(self, title=None, elapsed=None, total=None, playing=None):
        if title is not None:
            self.title = title
        if elapsed is not None:
            self.elapsed = elapsed
        if total is not None:
            self.total = total
        if playing is not None:
            self.playing = playing
        self.update()

    def set_volume(self, value):
        self.volume = value

    def _animate(self):
        if not self.playing:
            self.bars = [0.0] * 14
            self._tick = 0
            return
        self._tick += 1
        for i in range(14):
            wave = (0.5 + 0.5 * math.sin(self._tick * 0.27 + i * 0.6)) * 0.55
            noise = random.random() * 0.38
            self.bars[i] = max(0.04, min(1.0, wave + noise))
        self.update()

    @staticmethod
    def _fmt(seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            pxfill(p, 0, 0, self.width(), self.height(), LED_BG)
            p.setPen(EDGE)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(self.rect().adjusted(0, 0, -1, -1))

            # --- Statuszeile (zentriert) ---
            status = "PLAY" if self.playing else "STBY"
            sstr = f"{status}  VOL {self.volume:02d}  STEREO"
            sw = bit_text_width(sstr, 3)
            draw_bit_text(p, sstr, (self.width() - sw) // 2, 12, NEON_GREEN, 3)

            # --- Equalizer (blockig, gruen->gelb->rot, zentriert) ---
            maxh = 40
            baseline = 108
            eq_w = 14 * 18 - 6
            eq_x = (self.width() - eq_w) // 2
            for i, v in enumerate(self.bars):
                x = eq_x + i * 18
                blocks = int(v * (maxh // 4))
                for b in range(blocks):
                    col = NEON_GREEN
                    if b >= 6:
                        col = NEON_YELLOW
                    if b >= 8:
                        col = EQ_RED
                    pxfill(p, x, baseline - (b + 1) * 4, 12, 4, col)
                pxfill(p, x, baseline, 12, 3, GRID_DIM)

            # --- Marquee (scrollend, zentriert) ---
            title = self.title.upper()
            if self.playing and len(title) > 14:
                span = "  " + title + "  "
                off = (self._tick // 3) % len(span)
                shown = span[off:off + 14]
            else:
                shown = title[:14]
            mw = bit_text_width(shown, 4)
            draw_bit_text(p, shown, (self.width() - mw) // 2, 116, NEON_CYAN, 4)

            # --- Zeit (zentriert) ---
            tstr = f"TIME {self._fmt(self.elapsed)} / {self._fmt(self.total)}"
            tw = bit_text_width(tstr, 3)
            draw_bit_text(p, tstr, (self.width() - tw) // 2, 166, NEON_MAGENTA, 3)

            # --- Scanlines (dezent) ---
            for y in range(0, self.height(), 4):
                pxfill(p, 0, y, self.width(), 1, QColor(0, 0, 0, 42))
        finally:
            p.end()


class ReelWidget(QWidget):
    """Pixelart-Kassettenspule."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.speed = 0.0
        self.setFixedSize(56, 56)
        tm = QTimer(self)
        tm.timeout.connect(self._spin)
        tm.start(50)

    def _spin(self):
        self.angle += self.speed
        self.angle %= 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            cx, cy = self.width() // 2, self.height() // 2
            pixel_block_disc(p, cx, cy, 26, 21, REEL_BODY, REEL_RIM)
            pixel_block_disc(p, cx, cy, 12, 8, REEL_HUB, REEL_BG)
            for i in range(3):
                a = math.radians(self.angle + i * 120)
                x1 = cx + 8 * math.cos(a)
                y1 = cy + 8 * math.sin(a)
                x2 = cx + 24 * math.cos(a)
                y2 = cy + 24 * math.sin(a)
                pixel_line(p, int(x1), int(y1), int(x2), int(y2), NEON_GREEN, step=3, size=2)
        finally:
            p.end()


class PixelSlider(QWidget):
    """Horizontaler Pixel-Regler (Volume)."""

    valueChanged = Signal(int)

    def __init__(self, value=60, parent=None):
        super().__init__(parent)
        self._value = max(0, min(100, value))
        self._drag_active = False
        self.setFixedSize(280, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def value(self):
        return self._value

    def setValue(self, v):
        v = max(0, min(100, int(v)))
        if v != self._value:
            self._value = v
            self.valueChanged.emit(v)
            self.update()

    def _set_from_x(self, x):
        left = 52
        avail = self.width() - left - 58
        ratio = (x - left) / avail
        self.setValue(round(max(0.0, min(1.0, ratio)) * 100))

    def mousePressEvent(self, e):
        self._drag_active = True
        self._set_from_x(e.position().x())

    def mouseMoveEvent(self, e):
        if self._drag_active:
            self._set_from_x(e.position().x())

    def mouseReleaseEvent(self, e):
        self._drag_active = False

    def wheelEvent(self, e):
        self.setValue(self._value + (5 if e.angleDelta().y() > 0 else -5))

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

            draw_bit_text(p, "VOL", 8, 10, NEON_CYAN, 3)

            left, top = 52, 16
            width = self.width() - left - 12
            reserve = 58
            track = width - reserve
            n = 18
            gap = 4
            block = (track - (n - 1) * gap) // n
            fill = round(self._value / 100 * n)
            for i in range(n):
                x = left + i * (block + gap)
                col = GRID_DIM
                if i < fill:
                    frac = i / n
                    if frac > 0.75:
                        col = NEON_MAGENTA
                    elif frac > 0.5:
                        col = NEON_YELLOW
                    else:
                        col = NEON_GREEN
                pxfill(p, x, top, block, block, col)

            p.setPen(EDGE)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRect(left - 2, top - 2, track + 3, block + 3))

            vtext = f"{self._value:03d}"
            draw_bit_text(p, vtext, left + track + 12, 13, NEON_YELLOW, 2)
        finally:
            p.end()


class PlaylistWidget(QListWidget):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setSpacing(2)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(is_audio(u) for u in event.mimeData().urls()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = [u for u in event.mimeData().urls() if is_audio(u)]
        if urls:
            self.files_dropped.emit([u.toLocalFile() for u in urls])
            event.acceptProposedAction()


class BoomBox(QWidget):
    def __init__(self, player, audio_output):
        super().__init__()
        self.player = player
        self.audio = audio_output

        self.setWindowTitle("BOOMNOXX")
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(8)

        self.brand = PixelBrand()
        root.addWidget(self.brand, 0)

        self.playlist = PlaylistWidget()
        self.playlist.files_dropped.connect(self.add_files)
        self.playlist.itemDoubleClicked.connect(self._play_from_list)
        root.addWidget(self.playlist, 2)

        hint = QLabel("DRAG & DROP MP3 FILES  OR  PRESS [EJECT]")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        # ---------- Boombox-Front ----------
        box = QFrame()
        box.setObjectName("boombox")
        self._wire_drops(box)
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(14, 12, 14, 12)
        box_layout.setSpacing(10)

        center = QFrame()
        center.setObjectName("center")
        self._wire_drops(center)
        cl = QVBoxLayout(center)
        cl.setContentsMargins(10, 6, 10, 6)
        cl.setSpacing(8)

        self.led = LedDisplay()
        cl.addWidget(self.led)

        deck = QFrame()
        deck.setObjectName("deck")
        deck.setFixedHeight(84)
        dl = QHBoxLayout(deck)
        dl.setContentsMargins(8, 4, 8, 4)
        self.reel_left = ReelWidget()
        self.reel_right = ReelWidget()
        dl.addWidget(self.reel_left)
        tape = QLabel("STEREO\nPHASE")
        tape.setObjectName("tape")
        tape.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.addWidget(tape)
        dl.addWidget(self.reel_right)
        cl.addWidget(deck)

        btns = QHBoxLayout()
        btns.setSpacing(6)
        self.btn_prev = self._make_button("|<<", self._prev)
        self.btn_play = self._make_button("PLAY/PAUSE", self._toggle_play, big=True)
        self.btn_stop = self._make_button("STOP", self._stop)
        self.btn_next = self._make_button(">>|", self._next)
        self.btn_open = self._make_button("EJECT", self._open_files)
        for b in (self.btn_open, self.btn_prev, self.btn_play, self.btn_stop, self.btn_next):
            btns.addWidget(b)
        cl.addLayout(btns)

        knobs = QHBoxLayout()
        knobs.addStretch(1)
        self.volume_slider = PixelSlider(value=50)
        self.volume_slider.valueChanged.connect(self._set_volume)
        knobs.addWidget(self.volume_slider, 0, Qt.AlignmentFlag.AlignVCenter)
        knobs.addStretch(1)
        power = QLabel("POWER\n9V DC")
        power.setObjectName("knoblabel")
        power.setAlignment(Qt.AlignmentFlag.AlignCenter)
        knobs.addWidget(power, 0, Qt.AlignmentFlag.AlignVCenter)
        knobs.addSpacing(10)
        self.theme_btn = self._make_button("ARCADE", self._cycle_theme)
        self.theme_btn.setToolTip("THEME: arcade -> ubuntu -> phosphor -> bios")
        knobs.addWidget(self.theme_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        cl.addLayout(knobs)

        box_layout.addWidget(center)

        root.addWidget(box, 3)

        self._set_volume(50)

        self.player.positionChanged.connect(
            lambda ms: self.led.set_info(elapsed=int(ms / 1000))
        )
        self.player.durationChanged.connect(
            lambda ms: self.led.set_info(total=int(ms / 1000))
        )
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.errorOccurred.connect(self._on_error)

    def _wire_drops(self, widget):
        widget.dragEnterEvent = self._drag_enter
        widget.dropEvent = self._drop

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop(self, event):
        urls = [u for u in event.mimeData().urls() if is_audio(u)]
        if urls:
            self.add_files([u.toLocalFile() for u in urls])
            event.acceptProposedAction()

    def _make_button(self, label, handler, big=False):
        b = QPushButton(label)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(handler)
        if big:
            b.setObjectName("play")
        return b

    # ---------- Themes ----------
    def _apply_theme(self, name):
        apply_theme(name)
        self.setStyleSheet(STYLESHEET)
        self.theme_btn.setText(name.upper())
        self.led.update()
        self.reel_left.update()
        self.reel_right.update()
        self.brand.update()
        self.volume_slider.update()

    def _cycle_theme(self):
        idx = (THEME_ORDER.index(self.theme_btn.text().lower()) + 1) % len(THEME_ORDER)
        self._apply_theme(THEME_ORDER[idx])

    # ---------- Playlist / Audio ----------
    def add_files(self, paths):
        have = {self.playlist.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.playlist.count())}
        added = False
        for path in paths:
            if not any(path.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
                continue
            if path in have:
                continue
            item = QListWidgetItem(path.split("/")[-1])
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.playlist.addItem(item)
            have.add(path)
            added = True
        if added and self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self._play_from_list(self.playlist.item(0))

    def _play_from_list(self, item):
        if item is None:
            return
        path = item.data(Qt.ItemDataRole.UserRole)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()
        self.playlist.setCurrentRow(self.playlist.row(item))
        self.led.set_info(title=path.split("/")[-1], playing=True)
        self.reel_left.speed = 4.0
        self.reel_right.speed = 4.0

    def _toggle_play(self):
        st = self.player.playbackState()
        if st == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        elif self.player.source().isEmpty() and self.playlist.count():
            self._play_from_list(self.playlist.currentItem() or self.playlist.item(0))
        else:
            self.player.play()

    def _stop(self):
        self.player.stop()
        self.reel_left.speed = 0.0
        self.reel_right.speed = 0.0

    def _next(self):
        self._step(1)

    def _prev(self):
        self._step(-1)

    def _step(self, direction):
        if not self.playlist.count():
            return
        row = self.playlist.currentRow()
        if row < 0:
            row = 0
        row = (row + direction) % self.playlist.count()
        self._play_from_list(self.playlist.item(row))

    def _open_files(self):
        music = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.MusicLocation)
        start_dir = music[0] if music else QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.HomeLocation
        )
        files, _ = QFileDialog.getOpenFileNames(
            self, "MP3-Dateien wählen", start_dir,
            "Audio (*.mp3 *.wav *.ogg *.flac *.m4a *.aac)",
        )
        if files:
            self.add_files(files)

    def _set_volume(self, value):
        self.audio.setVolume(value / 100.0)
        self.led.set_volume(value)

    def _on_state(self, state):
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.led.set_info(playing=playing)
        self.reel_left.speed = 4.0 if playing else 0.0
        self.reel_right.speed = 4.0 if playing else 0.0

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._step(1)

    def _on_error(self, error, msg):
        self.led.set_info(title=f"ERROR: {str(msg)[:26]}", playing=False)


class PixelBrand(QWidget):
    """Neon-Schriftzug in wechselnden Pixel-Farben."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            text = "BOOMNOXX"
            colors = (NEON_CYAN, NEON_MAGENTA, NEON_YELLOW)
            total = bit_text_width(text, 3)
            x = (self.width() - total) // 2
            for i, ch in enumerate(text):
                draw_bit_text(p, ch, x, 9, colors[i % 3], 3)
                x += 6 * 3
        finally:
            p.end()


def main():
    app = QApplication(sys.argv)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Round)
    app.setApplicationName("BoomNoxx")

    player = QMediaPlayer()
    audio = QAudioOutput()
    player.setAudioOutput(audio)

    win = BoomBox(player, audio)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()