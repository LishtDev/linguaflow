# Limitations connues

Ce document liste honnêtement les limites de la version actuelle, leur impact et
les contournements possibles.

## 1. Qualité de traduction

| Domaine | Limitation | Impact | Remède |
|---|---|---|---|
| Expressions idiomatiques | Le moteur local traduit au mot à mot (ex. « get the ball rolling ») | Moyen | Ajouter le terme au glossaire |
| Termes métier | Vocabulaire générique par défaut | Moyen | Glossaire personnalisé |
| Qualité globale | Dépend du modèle Argos (plus léger qu'un LLM) | Moyen | Activer un moteur en ligne si autorisé |
| Noms propres ambigus | Peuvent être traduits à tort | Faible | Ajouter en « terme protégé » |

## 4.2. Formats

| Format | Limitation | Impact | Remède |
|---|---|---|---|
| PDF scanné | OCR qualité variable | Moyen | Tesseract + relecture manuelle |
| PDF complexe (colonnes, tableaux) | Mise en page partielle | Moyen | Vérifier le rendu ; préférer DOCX/HTML si possible |
| PDF | Texte long peut déborder du bloc | Faible | Ajustement automatique de la taille ; vérifier visuellement |
| DOC (ancien) | Nécessite LibreOffice | Moyen | `sudo apt install libreoffice` ou convertir en `.docx` |
| Images | Pas de reconstruction visuelle | Faible | Export texte prioritaire ; utiliser l'original pour la mise en page |
| PPTX SmartArt / graphiques | Non traduits | Faible | Traduire manuellement ces objets |
| XLSX `.xlsm` | Macros non modifiées/exécutées | — | Comportement volontaire (sécurité) |
| EPUB | DRM non supportés | Faible | Retirer le DRM légalement avant usage |
| SRT/VTT | Sous-titres trop rapides après allongement | Faible | Avertissement affiché ; ajuster les timings à la main |

## 4.3. Moteur et confidentialité

| Domaine | Limitation | Impact | Remède |
|---|---|---|---|
| Moteur local | Paires de langues limitées aux modèles installés | Moyen | Installer la paire Argos voulue, ou moteur en ligne |
| Moteur en ligne | Nécessite un consentement explicite | — | Comportement volontaire (confidentialité) |
| Qualité idiomatique | Le local ne reformule pas les expressions | Moyen | Glossaire + correction linguistique |

## 4.4. Performances

| Domaine | Limitation | Impact | Remède |
|---|---|---|---|
| Très gros fichiers (>50 Mo) | Refusés par défaut | Faible | Découper, ou augmenter `MAX_FILE_SIZE_MB` |
| Nombre de tâches simultanées | 2 workers par défaut | Faible | Ajuster `JOBS_MAX_WORKERS` |
| Traitement long | Verrou de 30 min (`MAX_PROCESSING_SECONDS`) | Faible | Reprise possible après interruption |

## 4.5. Sécurité (by design)

- Serveur lié à `127.0.0.1` uniquement.
- Aucun transfert externe sans consentement explicite.
- Les originaux ne sont jamais supprimés automatiquement.
- Les clés d'API sont masquées dans l'interface et les journaux.
