# Installation sur Linux Mint

## 1. Prérequis système

- Python **3.11+** (Python 3.12 validé)
- `pip` et `venv`
- Paquets système optionnels selon les formats

```bash
# Base
sudo apt update
sudo apt install python3 python3-pip python3-venv

# OCR (images et PDF scannés) — optionnel
sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng

# Conversion .doc (ancien) — optionnel
sudo apt install libreoffice
```

## 2. Récupération du projet

```bash
cd ~/Documents
# (décompresser ou cloner le dossier linguaflow)
cd linguaflow
```

## 4.2. Dépendances Python

### Environnement virtuel (recommandé)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Installation système (si environnement géré)
Sur Debian/Ubuntu/Mint, pip peut exiger :
```bash
python3 -m pip install --break-system-packages -r requirements.txt
```

## 3. Modèle de traduction local (une seule fois)

Argos Translate nécessite un modèle par paire de langues. Pour anglais → français :

```bash
python3 - <<'PY'
import argostranslate.package as p
p.update_package_index()
pkgs = p.get_available_packages()
pkg = next(x for x in pkgs if x.from_code == "en" and x.to_code == "fr")
p.install_from_path(pkg.download())
print("Modèle en->fr installé")
PY
```

> Sans modèle local, configurez un moteur en ligne (facultatif) ou l'application
> signalera une erreur claire.

## 4. OCR (facultatif)
```bash
sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng
python3 -m pip install pytesseract Pillow
```
Sans OCR, les images et PDF scannés renvoient une erreur explicite (le reste
fonctionne).

## 5. Lancement

```bash
./scripts/start.sh
# ou
python3 run.py
# ou, en développement
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Ouvrir ensuite : **http://127.0.0.1:8000**

## 6. Arrêt
`Ctrl+C` dans le terminal, ou :
```bash
pkill -f "uvicorn app.main:app"
```

## 7. Vérification

```bash
python3 -c "from app.main import app; print('OK', app.title)"
python3 -m pytest tests/ -q
```

## 8. Données et sauvegarde
Toutes les données sont dans `data/`. Voir
`docs/sauvegarde_maintenance.md`.

## 9. Dépannage
Voir `docs/diagnostic_erreurs.md`.
