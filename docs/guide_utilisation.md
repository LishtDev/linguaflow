# Guide d'utilisation — LinguaFlow

Ce guide décrit l'usage quotidien de l'application depuis l'interface web
(locale, en français). Aucune donnée ne quitte votre machine sauf si vous
activez explicitement un moteur en ligne.

## 1. Démarrer l'application

```bash
./scripts/start.sh
# ou
python3 run.py
```

Ouvrez ensuite http://127.0.0.1:8000 dans votre navigateur.

L'interface comporte cinq pages :

| Page | Rôle |
|---|---|
| **Accueil** | Import et lancement des traductions |
| **Détail d'une tâche** | Progression, aperçu, reprise, téléchargement |
| `Historique` | Toutes les tâches passées + suppression |
| `Paramètres` | Moteurs, consentement, langues, correction |
| `Glossaire` | Termes imposés et éléments protégés |

## 2. Traduire un fichier

1. Sur la page d'accueil, **glissez-déposez** un ou plusieurs fichiers, ou
   cliquez pour parcourir.
2. Choisissez la **langue source** (ou laissez « Détection automatique »).
   La langue cible est le français.
2. (Option) Cochez « Correction linguistique » pour appliquer une relecture
   typographique française automatique.
3. Lancez la traduction. Chaque fichier crée une tâche suivie dans l'historique.

La progression s'affiche en temps réel (segments traités / total). Vous pouvez
quitter l'onglet : le traitement continue en arrière-plan.

### Formats pris en charge
TXT, Markdown, HTML, CSV/TSV, DOCX, DOC, PPTX, XLSX, PDF, EPUB, SRT/VTT,
images (JPG, JPEG, PNG, TIF, TIFF, BMP — via OCR).

## 2.1 Éléments protégés automatiquement

Pendant la traduction, LinguaFlow **ne traduit jamais** :

- blocs et extraits de code (`` ` `` et ``` ``` `` ``, `` `...` ``) ;
- URLs, adresses e-mail, adresses IP ;
- chemins de fichiers Unix/Windows ;
- numéros de version, noms de fichiers techniques ;
- identifiants `snake_case`, appels `fonction()`, formules Excel.

Ces éléments sont réinsérés **à l'identique** dans le document final, même si
le moteur altère les jetons internes (stratégie de repli par tranches).

## 2.2 Reprise après interruption
Si l'application est fermée en cours de traitement, les tâches sont marquées
« interrompue ». Rouvrez la tâche puis cliquez sur **Reprendre** : seuls les
segments non traduits seront retraités.

## 3. Résultat
Une fois la tâche terminée, bouton **Télécharger** pour récupérer le fichier
traduit dans le même format que l'original. Un aperçu texte est disponible.

## 4. Glossaire et termes protégés
- **Entrées de glossaire** : imposent une traduction précise pour un terme
  (ex. « cloud computing » → « informatique en nuage »).
- **Termes protégés** : empêchent totalement la traduction d'un terme
  (marques, noms propres, identifiants).

## 5. Historique et reprise
- La page Historique liste les tâches avec statut, moteur, progression.
- Chaque tâche peut être consultée, téléchargée, relancée (reprise) ou supprimée.

## 6. Paramètres
- Choix du moteur : local (Argos) par défaut ; moteur en ligne facultatif.
- Activation du moteur en ligne : nécessite un consentement explicite et
  affiche un avertissement de confidentialité.
- Langue cible, langue source par défaut, correction, glossaire.
- Les clés d'API sont affichées masquées dans l'interface.

## 7. Confidentialité
- Le serveur écoute uniquement sur `127.0.0.1`.
- Aucun fichier n'est envoyé à l'extérieur sans consentement explicite.
- Les documents originaux ne sont jamais supprimés automatiquement.

## 8. Formats de sortie
Chaque format est reconstruit dans son format d'origine en préservant au mieux
la structure (styles, mise en page, cellules, formules, balises, scripts,
timestamps). Voir `docs/moteurs_et_formats.md` et `docs/limitations_connues.md`.
