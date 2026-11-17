#!/usr/bin/env bash
# One-time setup for a fresh cloud workspace. Run from anywhere; installs into $WORK (default /home/claude/work).
set -e
WORK=${WORK:-/home/claude/work}
mkdir -p "$WORK/tts" "$HOME/.fonts"
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq libcairo2-dev pkg-config ffmpeg >/dev/null 2>&1 || true
pip install -q --break-system-packages pycairo kokoro-onnx soundfile scipy numpy pillow 2>&1 | grep -v WARNING || true
cd "$HOME/.fonts"
[ -f "Fredoka%5Bwdth,wght%5D.ttf" ] || curl -sSfLO "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf"
[ -f "Baloo2%5Bwght%5D.ttf" ] || curl -sSfLO "https://raw.githubusercontent.com/google/fonts/main/ofl/baloo2/Baloo2%5Bwght%5D.ttf"
fc-cache -f >/dev/null
cd "$WORK/tts"
[ -f voices-v1.0.bin ] || curl -sSfL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
[ -f kokoro-v1.0.onnx ] || curl -sSfL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
python3 -c "import cairo, kokoro_onnx; print('setup ok')"
