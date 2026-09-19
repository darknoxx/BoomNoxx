#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS="$HOME/.local/share/applications"
DESKTOP="$APPS/boomnoxx.desktop"
VENV_PY="$DIR/.venv/bin/python"
APP="$DIR/main.py"

if [ "${1:-}" = "--uninstall" ]; then
    rm -f "$DESKTOP"
    update-desktop-database "$APPS" 2>/dev/null || true
    echo "Entfernt: $DESKTOP"
    exit 0
fi

if [ ! -x "$VENV_PY" ]; then
    echo "[setup] venv fehlt — lege sie an ..."
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Fehler: 'python3' ist nicht installiert."
        exit 1
    fi
    python3 -m venv "$DIR/.venv"
    echo "[setup] installiere Abhaengigkeiten (PySide6) ..."
    "$VENV_PY" -m pip install -r "$DIR/requirements.txt"
fi

if [ ! -f "$APP" ]; then
    echo "Fehler: main.py nicht gefunden ($APP)"
    exit 1
fi

gen() {
    cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=BoomNoxx
Comment=Retro-Pixel-MP3-Player
Exec=$VENV_PY $APP
Icon=$DIR/icon.svg
Terminal=false
Categories=Audio;Music;Player;
StartupNotify=true
Keywords=mp3;musik;boombox;retro;
EOF
}

mkdir -p "$APPS"
gen
chmod +x "$DESKTOP" 2>/dev/null || true
update-desktop-database "$APPS" 2>/dev/null || true
echo "Installiert: $DESKTOP"
echo "BoomNoxx erscheint jetzt im Dash / Anwendungsgrid."