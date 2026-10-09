#!/bin/bash
# LinguaFlow — nettoyage des données.
#
# Usage :
#   ./scripts/cleanup.sh --temp      # fichiers temporaires uniquement
#   ./scripts/cleanup.sh --results   # résultats générés
#   ./scripts/cleanup.sh --logs      # journaux
#   ./scripts/cleanup.sh --all       # tout ci-dessus (garde la base)
#   ./scripts/cleanup.sh --all --db  # tout, y compris la base (historique)
#
# Sans option : mode interactif.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="$ROOT/data"

DO_TEMP=0 DO_RESULTS=0 DO_LOGS=0 DO_DB=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --temp) DO_TEMP=1 ;;
    --results) DO_RESULTS=1 ;;
    --logs) DO_LOGS=1 ;;
    --db) DO_DB=1 ;;
    --all) DO_TEMP=1 DO_RESULTS=1 DO_LOGS=1 ;;
    *) echo "Option inconnue : $1" >&2; exit 2 ;;
  esac
  shift
done

if [[ $DO_TEMP -eq 0 && $DO_RESULTS -eq 0 && $DO_LOGS -eq 0 && $DO_DB -eq 0 ]]; then
  echo "Que nettoyer ?"
  read -rp "  fichiers temporaires [o/N] " a; [[ "${a:-n}" =~ ^[oO] ]] && DO_TEMP=1
  read -rp "  résultats [o/N] " b; [[ "${b:-n}" =~ ^[oO] ]] && DO_RESULTS=1
  read -rp "  journaux [o/N] " c; [[ "${b:-n}" =~ ^[oO] ]] && DO_LOGS=1
fi

rm_contents() {
  local dir="$1"
  if [[ -d "$DATA/$dir" ]]; then
    find "$DATA/$dir" -mindepth 1 -delete
    echo "  vidé : data/$dir"
  fi
}

[[ $DO_TEMP -eq 1 ]] && rm -rf "$DATA/temp" && mkdir -p "$DATA/temp" && echo "  supprimé : data/temp/"
[[ $DO_RESULTS -eq 1 ]] && { rm -rf "$DATA/results"; mkdir -p "$DATA/results"; echo "  vidé : data/results/"; }
if [[ $DO_LOGS -eq 1 ]]; then
  find "$DATA/logs" -type f -name '*.log' -delete 2>/dev/null || true
  echo "  journaux supprimés"
fi
if [[ $DO_DB -eq 1 ]]; then
  rm -f "$DATA/linguaflow.db"
  echo "  base de données supprimée (historique réinitialisé)"
fi

echo "Nettoyage terminé."
