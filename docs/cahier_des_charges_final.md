# LINGUAFLOW — CAHIER DES CHARGES FINAL

## 1. Objet
LinguaFlow est une application web **locale** (Linux Mint) qui traduit des
documents de formats variés vers un **français naturel** tout en préservant la
structure, la mise en page et les éléments techniques.

## 2. Exigences fonctionnelles et état de réalisation

| # | Exigence | État |
|---|---|---|
| F1 | Traduire TXT, MD, HTML, CSV/TSV | ✅ |
| F2 | Traduire DOCX, DOC, PPTX, XLSX | ✅ |
| F3 | Traduire PDF, EPUB | ✅ |
| F4 | Traduire sous-titres SRT/VTT | ✅ |
| F5 | Traduire images (OCR local) | ✅ (dépend de Tesseract) |
| F6 | Préserver structure, styles, formules, balises, scripts | ✅ |
| F7 | Protection réversible des éléments non traduisibles | ✅ |
| F8 | Détection automatique de la langue + choix manuel | ✅ |
| F9 | Correction linguistique française | ✅ |
| F10 | Glossaire et termes protégés | ✅ |
| F11 | Interruption / reprise des tâches | ✅ |
| F12 | Historique, téléchargement, suppression | ✅ |
| F13 | Moteur local par défaut, en ligne facultatif | ✅ |
| F14 | Aucun transfert sans consentement explicite | ✅ |
| F15 | Interface en français | ✅ |
| F16 | Tests automatisés | ✅ 73 tests |

## 3. Exigences non fonctionnelles

| # | Exigence | Réalisation |
|---|---|---|
| N1 | Confidentialité : local-first | Argos Translate, serveur `127.0.0.1` |
| N2 | Consentement explicite avant envoi externe | `remote_consent` |
| N3 | Sécurité : anti-traversée, assainissement des noms | `app/core/security.py` |
| N4 | Reproductibilité / tests | pytest, 73 cas |
| N4 | Robustesse des placeholders | fast-path + fallback par spans |
| N6 | Performances : tâches en arrière-plan | ThreadPoolExecutor (2 workers) |
| N7 | Traçabilité | Journaux avec masquage des secrets |

## 4. Architecture
- **Python 3.11+**, FastAPI + Jinja2 + JS natif, SQLite/SQLAlchemy.
- Modèle **Formatter** : un extracteur/reconstructeur par format.
- Pipeline : extraction → détection → sélection moteur → protection →
  traduction → correction → reconstruction → vérification.
- Travaux en arrière-plan via `ThreadPoolExecutor`.

## 4. Confidentialité
- Aucun fichier n'est envoyé à l'extérieur sans consentement explicite.
- Les documents originaux ne sont jamais supprimés automatiquement.

## 5. Livrables
- Code applicatif (`app/`).
- Interface web (`app/templates`, `app/static`).
- Scripts (`scripts/start.sh`, `backup.sh`, `cleanup.sh`,
  `generate_fixtures.py`).
- Documentation (`docs/`) et exemples (`examples/`).
- Tests (`tests/`, 73 cas).

## 6. Périmètre exclu (limitations assumées)
- Reconstitution visuelle des images (export texte uniquement).
- Traduction des macros et SmartArt.
- DRM EPUB.
- Fichiers > 50 Mo par défaut.

Voir `docs/limitations_connues.md` et `docs/moteurs_et_formats.md`.
