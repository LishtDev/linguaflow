#!/bin/bash
# LinguaFlow — sauvegarde des données (base, résultats, configuration).
#
# Usage :
#   ./scripts/backup.sh [destination]
#
# Par défaut la sauvegarde est créée dans backup/linguaflow_AAAAMMJJ-HHMMSS.tar.gz
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="$ROOT/data"
DEST="${1:-$ROOT/backup}"
STAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="$DEST/linguaflow_$STAMP.tar.gz"

mkdir -p "$DEST"

echo "Sauvegarde de LinguaFlow vers $ARCHIVE"
tar -czf "$ARCHIVE" \
  -C "$ROOT" \
  --exclude='data/temp' \
  --exclude='data/cache' \
  --exclude='data/logs/*.log' \
  data

echo "Terminé : $ARCHIVE"
echo "Restauration : tar -xzf '$ARCHIVE' -C '$ROOT'"
