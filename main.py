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
    QLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}

# --- Monochrom (Schwarz / Weiss) ---
LINE = QColor("#f5f5f5")
FG = QColor("#f2f2f2")
SOFT = QColor("#8a8a8a")
DIM = QColor("#2e2e2e")
LED_BG = QColor("#050505")
EQ_LO = QColor("#555555")
EQ_MID = QColor("#9a9a9a")
EQ_HI = FG
REEL_BODY = QColor("#f2f2f2")
REEL_RIM = QColor("#2e2e2e")
REEL_HUB = QColor("#050505")
REEL_BG = QColor("#0a0a0a")

STYLESHEET = """
QWidget {
    background: #000000;
    color: #f2f2f2;
    font-family: "DejaVu Sans Mono", monospace;
    font-weight: bold;
    font-size: 12px;
}
QListWidget {
    background: #0f0f0f;
    border: 2px solid #f2f2f2;
    border-radius: 0;
    padding: 4px;
    color: #f2f2f2;
}
QListWidget::item {
    padding: 4px 8px;
    border: 1px solid #2e2e2e;
    background: #1a1a1a;
}
QListWidget::item:selected {
    background: #f2f2f2;
    color: #000000;
}
QFrame#boombox {
    background: #0f0f0f;
    border: 2px solid #f2f2f2;
    border-radius: 0;
}
QFrame#center { background: transparent; border: none; }
QFrame#deck {
    background: #000000;
    border: 2px solid #2e2e2e;
    border-radius: 0;
}
QLabel#hint {
    color: #8a8a8a;
    font-size: 11px;
    letter-spacing: 2px;
}
QLabel#tape {
    color: #f2f2f2;
    font-size: 12px;
    letter-spacing: 2px;
    background: transparent;
}
QLabel#knoblabel {
    color: #8a8a8a;
    font-size: 11px;
    letter-spacing: 2px;
    background: transparent;
}
QPushButton {
    background: #000000;
    border: 2px solid #f2f2f2;
    border-radius: 0;
    padding: 6px 8px;
    color: #f2f2f2;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background: #1a1a1a;
    border-color: #ffffff;
}
QPushButton:pressed {
    background: #f2f2f2;
    color: #000000;
    padding: 7px 7px 5px 9px;
}
QPushButton#play {
    background: #f2f2f2;
    border-color: #ffffff;
    color: #000000;
}
QPushButton#play:hover { background: #e0e0e0; border-color: #ffffff; }
QPushButton#play:pressed { background: #bdbdbd; color: #000000; }
"""
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
            p.setPen(LINE)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(self.rect().adjusted(0, 0, -1, -1))

            # --- Statuszeile (zentriert) ---
            status = "PLAY" if self.playing else "STBY"
            sstr = f"{status}  VOL {self.volume:02d}  STEREO"
            sw = bit_text_width(sstr, 3)
            draw_bit_text(p, sstr, (self.width() - sw) // 2, 12, FG, 3)

            # --- Equalizer (blockig, grau gestuft: dunkel -> hell) ---
            maxh = 40
            baseline = 108
            eq_w = 14 * 18 - 6
            eq_x = (self.width() - eq_w) // 2
            for i, v in enumerate(self.bars):
                x = eq_x + i * 18
                blocks = int(v * (maxh // 4))
                for b in range(blocks):
                    col = EQ_LO
                    if b >= 3:
                        col = EQ_MID
                    if b >= 6:
                        col = EQ_HI
                    pxfill(p, x, baseline - (b + 1) * 4, 12, 4, col)
                pxfill(p, x, baseline, 12, 3, DIM)

            # --- Marquee (scrollend, zentriert) ---
            title = self.title.upper()
            if self.playing and len(title) > 14:
                span = "  " + title + "  "
                off = (self._tick // 3) % len(span)
                shown = span[off:off + 14]
            else:
                shown = title[:14]
            mw = bit_text_width(shown, 4)
            draw_bit_text(p, shown, (self.width() - mw) // 2, 116, FG, 4)

            # --- Zeit (zentriert) ---
            tstr = f"TIME {self._fmt(self.elapsed)} / {self._fmt(self.total)}"
            tw = bit_text_width(tstr, 3)
            draw_bit_text(p, tstr, (self.width() - tw) // 2, 166, SOFT, 3)

            # --- Scanlines (dezent) ---
            for y in range(0, self.height(), 4):
                pxfill(p, 0, y, self.width(), 1, QColor(0, 0, 0, 42))
        finally:
            p.end()


class MiniLed(QWidget):
    """Kompakte Pixel-LED fuer den Mini-Modus."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "INSERT TAPE "
        self.playing = False
        self.volume = 50
        self._tick = 0
        self.setFixedHeight(52)
        self.setMinimumWidth(200)
        tm = QTimer(self)
        tm.timeout.connect(self._animate)
        tm.start(60)

    def set_info(self, title=None, playing=None):
        if title is not None:
            self.title = title
        if playing is not None:
            self.playing = playing
        self.update()

    def set_volume(self, value):
        self.volume = value
        self.update()

    def _animate(self):
        if self.playing:
            self._tick += 1
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            pxfill(p, 0, 0, self.width(), self.height(), LED_BG)
            p.setPen(LINE)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(self.rect().adjusted(0, 0, -1, -1))

            status = "PLAY" if self.playing else "STBY"
            s = 3 if self.width() >= 280 else 2 if self.width() >= 200 else 1
            sstr = f"{status}  VOL {self.volume:02d}"
            sw = bit_text_width(sstr, s)
            draw_bit_text(p, sstr, (self.width() - sw) // 2, 6, SOFT, s)

            title = self.title.upper()
            shown_len = max(4, (self.width() - 24) // (6 * s - 1))
            if self.playing and len(title) > shown_len:
                span = "  " + title + "  "
                off = (self._tick // 3) % len(span)
                shown = span[off:off + shown_len]
            else:
                shown = title[:shown_len]
            mw = bit_text_width(shown, s)
            draw_bit_text(p, shown, (self.width() - mw) // 2, 10 + s * 7, FG, s)

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
                pixel_line(p, int(x1), int(y1), int(x2), int(y2), SOFT, step=3, size=2)
        finally:
            p.end()


class PixelSlider(QWidget):
    """Horizontaler Pixel-Regler (Volume)."""

    valueChanged = Signal(int)

    def __init__(self, value=60, width=280, parent=None):
        super().__init__(parent)
        self._value = max(0, min(100, value))
        self._drag_active = False
        if width >= 240:
            self._left, self._reserve, self._n, self._gap = 52, 58, 18, 4
        else:
            self._left, self._reserve, self._n, self._gap = 40, 44, 12, 3
        self.setFixedSize(width, 40)
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
        ratio = (x - self._left) / (self.width() - self._left - self._reserve)
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

            if self.width() >= 240:
                draw_bit_text(p, "VOL", 8, 10, SOFT, 3)

            left, top = self._left, 16
            width = self.width() - left - 12
            reserve = self._reserve
            track = width - reserve
            n = self._n
            gap = self._gap
            block = (track - (n - 1) * gap) // n
            fill = round(self._value / 100 * n)
            for i in range(n):
                x = left + i * (block + gap)
                col = DIM
                if i < fill:
                    col = EQ_MID if i / n > 0.6 else FG
                pxfill(p, x, top, block, block, col)

            p.setPen(LINE)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRect(left - 2, top - 2, track + 3, block + 3))

            vtext = f"{self._value:03d}"
            draw_bit_text(p, vtext, left + track + 12, 13, FG, 2)
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
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self._stack = QStackedLayout()
        root.addLayout(self._stack)

        # ---------- Standardseite ----------
        normal = QWidget()
        self._normal_page = normal
        self._wire_drops(normal)
        nl = QVBoxLayout(normal)
        nl.setContentsMargins(16, 12, 16, 16)
        nl.setSpacing(8)

        self.brand = PixelBrand()
        nl.addWidget(self.brand, 0)

        self.playlist = PlaylistWidget()
        self.playlist.files_dropped.connect(self.add_files)
        self.playlist.itemDoubleClicked.connect(self._play_from_list)
        nl.addWidget(self.playlist, 2)

        hint = QLabel("DRAG & DROP MP3 FILES  OR  PRESS [EJECT]")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nl.addWidget(hint)

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
        self.btn_play = self._make_button("PLAY", self._toggle_play, big=True)
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
        self.btn_mini = self._make_button("MINI", self._go_compact)
        knobs.addWidget(self.btn_mini, 0, Qt.AlignmentFlag.AlignVCenter)
        cl.addLayout(knobs)

        box_layout.addWidget(center)

        nl.addWidget(box, 3)

        # ---------- Kompaktseite ----------
        compact = QWidget()
        self._compact_page = compact
        self._wire_drops(compact)
        cl2 = QHBoxLayout(compact)
        cl2.setContentsMargins(10, 8, 10, 8)
        cl2.setSpacing(8)

        self.btn_expand = self._make_button("EXPAND", self._go_normal)
        cl2.addWidget(self.btn_expand)

        self.mini_led = MiniLed()
        cl2.addWidget(self.mini_led, 1)

        self.btn_mini_prev = self._make_button("|<<", self._prev)
        self.btn_mini_play = self._make_button("PLAY", self._toggle_play, big=True)
        self.btn_mini_next = self._make_button(">>|", self._next)
        for b in (self.btn_mini_prev, self.btn_mini_play, self.btn_mini_next):
            cl2.addWidget(b)

        self.compact_volume = PixelSlider(value=50, width=170)
        self.compact_volume.valueChanged.connect(self._set_volume)
        cl2.addWidget(self.compact_volume, 0, Qt.AlignmentFlag.AlignVCenter)

        self._stack.addWidget(normal)
        self._stack.addWidget(compact)
        self._stack.setCurrentIndex(0)

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

        self.adjustSize()

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

    # ---------- Modus-Umschaltung ----------
    def _frame_delta(self):
        return self.frameGeometry().size() - self.size()

    def _go_compact(self):
        self._normal_geometry = self.geometry()
        self._stack.setCurrentWidget(self._compact_page)
        self.setWindowTitle("BOOMNOXX · MINI")
        d = self._frame_delta()
        self.resize(
            self._compact_page.sizeHint().width() + d.width(),
            self._compact_page.sizeHint().height() + d.height(),
        )

    def _go_normal(self):
        self._stack.setCurrentWidget(self._normal_page)
        self.setWindowTitle("BOOMNOXX")
        if getattr(self, "_normal_geometry", None):
            self.setGeometry(self._normal_geometry)
        else:
            self.adjustSize()

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
        self.mini_led.set_info(title=path.split("/")[-1], playing=True)
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
        self.mini_led.set_volume(value)
        for s in (self.volume_slider, self.compact_volume):
            if s.value() != value:
                s.setValue(value)

    def _on_state(self, state):
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.led.set_info(playing=playing)
        self.mini_led.set_info(playing=playing)
        self.reel_left.speed = 4.0 if playing else 0.0
        self.reel_right.speed = 4.0 if playing else 0.0
        label = "PAUSE" if playing else "PLAY"
        self.btn_play.setText(label)
        self.btn_mini_play.setText(label)

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._step(1)

    def _on_error(self, error, msg):
        self.led.set_info(title=f"ERROR: {str(msg)[:26]}", playing=False)
        self.mini_led.set_info(title=f"ERROR: {str(msg)[:26]}", playing=False)


class PixelBrand(QWidget):
    """Schriftzug im monochromen Pixel-Stil."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            text = "BOOMNOXX"
            colors = (FG, SOFT, FG)
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