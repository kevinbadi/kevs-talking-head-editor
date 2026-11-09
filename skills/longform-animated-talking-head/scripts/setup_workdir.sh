#!/usr/bin/env bash
# Create projects/<slug>-longform/ and copy the engine + shared modules + fonts + Claude marks.
#   bash .../scripts/setup_workdir.sh <slug>      (run from your workspace root, or set PROJECTS_ROOT)
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="${PROJECTS_ROOT:-$PWD}"                     # workspace root (projects/ is created here)
SLUG="${1:?slug}"
WD="$ROOT/projects/${SLUG}-longform"
mkdir -p "$WD"/{source,audio,renders,frames,fonts,assets/logos,assets/gifs,assets/figures,assets/thumbs,assets/shots}
cp "$SKILL"/templates/{longform_engine,media_marks,hyper_edits,light_fx,fonts,claude_marks,flow_diagram}.py "$WD/"
cp "$SKILL"/templates/fonts/*.ttf "$WD/fonts/"
cp "$SKILL"/assets/claude-*.png "$WD/assets/"
[ -f "$WD/render.py" ] || cp "$SKILL/templates/render_template.py" "$WD/render.py"
echo "workdir: $WD"
