# LinguaFlow

Application web **locale** (Linux Mint) pour traduire des documents de formats
variés vers un **français naturel**, en préservant la structure, la mise en page
et les éléments techniques.

Conçue **confidentialité d'abord** : le moteur local (Argos Translate) est
utilisé par défaut et **aucun fichier n'est envoyé à l'extérieur sans
consentement explicite**.

## Fonctionnalités

- Traduction de : TXT, Markdown, HTML, CSV/TSV, DOCX, DOC, PPTX, XLSX, PDF,
  EPUB, SRT/VTT et images (OCR).
- Préservation de la structure : styles, tableaux, formules, balises, scripts,
  horodatages, images.
- Protection **réversible** des éléments non traduisibles (code, URL, e‑mails,
  chemins, versions, identifiants, formules Excel).
- Détection automatique de la langue + sélection manuelle.
- Correction linguistique française (typographie).
- Glossaire et termes protégés.
- Interruption / **reprise** des tâches, historique, téléchargement.
- Moteur local par défaut ; moteur en ligne facultatif avec consentement.

## Démarrage rapide

```bash
python3 -m pip install -r requirements.txt   # dépendances
./scripts/start.sh                            # lancement
# → http://127.0.0.1:8000
```

Installation détaillée : [`docs/installation_linux_mint.md`](docs/installation_linux_mint.md).

## Structure du projet

```
app/
  core/          configuration, base de données, sécurité, logs, exceptions
  models/        modèles SQLAlchemy (tâches, segments, glossaire)
  routes/        points d'entrée HTTP (pages + API REST)
  schemas/       schémas Pydantic
  services/      logique métier
    formatters/  un formateur par format (extract / reconstruct)
    translation/ moteurs (Argos local, LibreTranslate distant)
    protection/  protection réversible des éléments techniques
    correction/  correction linguistique française
    ocr/         OCR local (Tesseract)
  templates/     gabarits Jinja2 (interface FR)
  static/        CSS + JavaScript
  workers/       file de tâches en arrière-plan
tests/           tests unitaires et d'intégration (73 cas)
scripts/         start.sh, backup.sh, cleanup.sh, generate_fixtures.py
docs/            documentation complète
examples/        exemples de fichiers à traduire
data/            base, résultats, temporaires, journaux (généré)
```

## Tests

```bash
python3 -m pytest tests/ -q          # suite complète
python3 -m pytest tests/unit -q      # tests unitaires
python3 -m pytest tests/integration  # tests d'intégration (API + pipeline)
```

Les tests utilisent un moteur simulé (`MockTranslator`) : ils ne nécessitent
aucun modèle ni accès réseau.

## Documentation

- [Guide d'utilisation](docs/guide_utilisation.md)
- [Installation Linux Mint](docs/installation_linux_mint.md)
- [Moteurs et formats](docs/moteurs_et_formats.md)
- [Limitations connues](docs/limitations_connues.md)
- [Diagnostic des erreurs](docs/diagnostic_erreurs.md)
- [Sauvegarde et maintenance](docs/sauvegarde_maintenance.md)
- [Cahier des charges final](docs/cahier_des_charges_final.md)

## Confidentialité

- Serveur lié à `127.0.0.1` uniquement.
- Moteur local par défaut ; moteur en ligne désactivé sans consentement.
- Clés d'API masquées dans l'interface et les journaux.

## Licence

MIT
