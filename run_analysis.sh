#!/bin/bash
# Script wrapper pour forcer l'encodage UTF-8

# Forcer les locales UTF-8
export LC_ALL=fr_FR.UTF-8
export LANG=fr_FR.UTF-8
export PYTHONIOENCODING=UTF-8

# Se placer dans le bon répertoire
cd "$(dirname "$0")"

# Lancer le script Python avec les arguments passés
python3 scripts/generate_analysis_batch.py "$@"


