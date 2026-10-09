# Moteurs de traduction et formats supportés

## 1. Moteurs de traduction

LinguaFlow combine deux familles de moteurs, sélectionnées automatiquement
selon la disponibilité et la politique de confidentialité.

### 1.1 Moteur local — Argos Translate (par défaut)
- **Fonctionne hors ligne**, aucune donnée ne quitte la machine.
- Modèles neuronaux (OpenNMT/ctranslate2) par paire de langues.
- Installation d'une paire (une fois, avec Internet) :

```bash
python3 - <<'PY'
import argostranslate.package as p
p.update_package_index()
pkg = next(x for x in p.get_available_packages()
           if x.from_code == "en" and x.to_code == "fr")
p.install_from_path(pkg.download())
PY
```

## 2. Sélection du moteur

Ordre de décision (`EngineManager`) :
1. Moteur local (Argos) si la paire de langues est disponible.
2. Sinon, moteur en ligne **uniquement** si activé **et** consenti.
- Sinon : erreur explicite, aucun transfert non autorisé.

## 3. Moteurs en ligne (facultatif, désactivé par défaut)
- API compatible LibreTranslate.
- Désactivé par défaut. Activation en deux étapes :
  1. `remote_enabled = true` (Paramètres).
  2. **Consentement explicite** (`remote_consent`) — un message avertit que le
     contenu sera envoyé à un service tiers.
- Les clés d'API sont masquées à l'affichage et dans les journaux.

## 2. Tableau des formats

| Format | Ext. | Extraction | Préservation | Limites |
|---|---|---|---|---|
| Texte brut | `.txt` | lignes | sauts de ligne, encodage, BOM | aucun style |
| Markdown | `.md`, `.markdown` | prose hors code | syntaxe, blocs de code, liens, titres | tableaux complexes |
| HTML | `.html`, `.htm` | texte visible + attributs (`title`, `alt`, `placeholder`, `aria-*`) | balises, scripts, styles | aucun rendu JS |
| CSV/TSV | `.csv`, `.tsv` | cellules texte | délimiteur, encodage, colonnes, nombres | grandes tables |
| DOCX | `.docx` | paragraphes, tableaux, en-têtes/pieds | styles, images, mise en page | champs (`MERGEFIELD`) non traduits |
| DOC | `.doc` | conversion via LibreOffice | autant que .docx | **LibreOffice requis** |
| PPTX | `.pptx` | cadres texte, titres, tableaux, notes | disposition, images, ordre des diapos | SmartArt non traduit |
| XLSX | `.xlsx` | valeurs texte uniquement | formules, nombres, formats, feuilles | macros `.xlsm` non exécutées |
| PDF | `.pdf` | blocs de texte positionnés | position, taille de police ajustée | PDF **scannés** → OCR ; colonnes complexes |
| EPUB | `.epub` | XHTML des chapitres | CSS, images, structure du conteneur | DRM non supportés |
| SRT / VTT | `.srt`, `.vtt` | texte des sous-titres | horodatages, structure des blocs | limites de vitesse de lecture signalées |
| Images | `.png .jpg .jpeg .tif .tiff .bmp` | OCR local (Tesseract) | export du texte traduit | **Tesseract requis** ; reconstitution visuelle non proposée |

## 2. Protection des éléments techniques
Tous formats confondus, les éléments suivants sont protégés puis restaurés
verbatim : blocs/inline `code`, URL, e‑mails, chemins, versions, IP, noms de
fichiers techniques, identifiants `snake_case`, appels `f()`, formules Excel.

## 3. Ajouter un moteur en ligne
1. Renseigner l'URL du service LibreTranslate et la clé éventuelle dans
   Paramètres.
2. Activer + consentir.
3. `EngineManager` l'expose automatiquement dans la liste des moteurs.

## 4. Ajouter un format
Implémenter `FormatterInterface` (`extract` / `reconstruct`) puis l'enregistrer
dans `app/services/formatters/registry.py`.
