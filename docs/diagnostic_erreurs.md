# Diagnostic et résolution des erreurs

Ce document liste les erreurs courantes, leur cause probable et la solution.

## 1. Démarrage de l'application

### `Address already in use` (port 8000 occupé)
Un autre processus utilise le port.

```bash
# Identifier le processus
ss -ltnp | grep 8000
# Ou lancer sur un autre port
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

### `ModuleNotFoundError: No module named 'app'`
Le répertoire courant n'est pas la racine du projet.

```bash
cd /chemin/vers/linguaflow
python3 run.py
```

### Modèles de traduction absents (Argos)
Symptôme : la traduction échoue avec une erreur de paire de langues.
Installer la paire requise (une seule fois, nécessite Internet) :

```bash
python3 - <<'PY'
import argostranslate.package as p
p.update_package_index()
pkgs = p.get_available_packages()
pkg = next(x for x in pkgs if x.from_code == "en" and x.to_code == "fr")
p.install_from_path(pkg.download())
PY
```

Sans modèle local et sans consentement pour le moteur en ligne, la tâche
échoue volontairement (aucun transfert non autorisé).

## 2. Téléversement

| Code | Erreur | Cause | Solution |
|---|---|---|---|
| 415 | `UnsupportedFormatError` | Extension non supportée | Vérifier `docs/moteurs_et_formats.md` |
| 413 | `FileTooLargeError` | Fichier > 50 Mo | Découper le fichier ou ajuster `MAX_FILE_SIZE_MB` |
| 400 | `FileValidationError` | Nom de fichier invalide / corrompu | Renommer, réessayer |

## 3. Extraction (lecture du document)

| Code | Erreur | Cause | Solution |
|---|---|---|---|
| 422 | `ExtractionError` (image/PDF scanné) | OCR indisponible | `sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng` puis `pip install pytesseract Pillow` |
| 422 | `ExtractionError` (.doc) | LibreOffice absent | `sudo apt install libreoffice` ou convertir en `.docx` |
| 422 | `ExtractionError` (PDF) | PDF corrompu ou protégé | Ouvrir/vérifier dans un lecteur, retirer la protection |

## 4. Traduction

| Erreur | Cause | Solution |
|---|---|---|
| `EngineUnavailableError` (503) | Moteur local non installé / en ligne désactivé | Installer Argos ou activer le moteur en ligne avec consentement |
| `RemoteEngineDisabledError` (403) | Moteur en ligne utilisé sans consentement | Cocher « J'autorise l'envoi » dans Paramètres |
| `TranslationError` (500) | Échec du moteur sur un segment | Relancer la tâche (reprise) ; consulter les logs |

## 5. Reconstruction (écriture du document)

| Erreur | Cause | Solution |
|---|---|---|
| `ReconstructionError` (500) | Fichier de sortie vide/illisible | Relancer ; vérifier l'espace disque |
| Fichier Office corrompu | Interruption pendant l'écriture | Utiliser la reprise, libérer de l'espace disque |

## 6. Où sont les journaux ?

```
data/logs/linguaflow.log
```

Les clés d'API et données sensibles y sont **masquées** automatiquement
(`app/core/logging_config.py::redact`).

## 7. Réinitialisation

Pour repartir d'une base propre (⚠️ supprime historique et résultats) :

```bash
./scripts/cleanup.sh --all
```

Voir `docs/sauvegarde_maintenance.md` pour une sauvegarde préalable.
