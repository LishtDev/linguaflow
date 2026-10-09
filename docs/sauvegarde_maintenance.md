# Sauvegarde et maintenance

## 1. Où sont stockées les données ?

Tout est contenu dans le dossier `data/` du projet :

| Chemin | Contenu | Sensible |
|---|---|---|
| `data/linguaflow.db` | Base SQLite : historique des tâches, segments, glossaire | Oui |
| `data/user_config.json` | Préférences (moteur, langue, consentement, clés API masquées) | Oui |
| `data/results/` | Documents traduits générés | Oui |
| `data/temp/` | Fichiers de travail temporaires | Non (jetables) |
| `data/models/` | Modèles de traduction locaux (Argos) | Non (retéléchargeables) |
| `data/cache/` | Caches divers | Non |
| `data/logs/` | Journaux d'exécution | Faible |

> ⚠️ Les **clés d'API** du moteur en ligne sont stockées dans
> `data/user_config.json`. Protégez ce fichier (droits `600`).

## 2. Sauvegarde

### Manuelle
```bash
./scripts/backup.sh
# ou vers un emplacement précis (disque externe)
./scripts/backup.sh /media/utilisateur/USB/sauvegardes
```

Le script crée une archive horodatée excluant temporaires, caches et journaux.

### À chaud
L'application peut rester en cours d'exécution : la base SQLite et les
résultats sont copiés tels quels. Évitez seulement de lancer une sauvegarde
pendant une écriture massive de résultats.

### Restauration
```bash
cd /chemin/vers/linguaflow
tar -xzf backup/linguaflow_AAAAMMJJ-HHMMSS.tar.gz
```

## 3. Nettoyage / maintenance

```bash
./scripts/cleanup.sh --temp       # fichiers temporaires
./scripts/cleanup.sh --results    # résultats générés
./scripts/cleanup.sh --logs       # journaux
./scripts/cleanup.sh --all        # temp + résultats + logs
./scripts/cleanup.sh --all --db   # tout + base (réinitialise l'historique)
```

Politique recommandée :
- Purger les temporaires régulièrement (`--temp`).
- Archiver puis purger les résultats anciens.
- Purger les journaux si volumineux.
- **Avant** un `--db`, toujours faire un `backup.sh`.

## 4. Rotation des journaux
Les journaux s'accumulent dans `data/logs/linguaflow.log`. Pour éviter une
croissance infinie, purger via `cleanup.sh --logs` ou configurer
`logrotate` :

```
# /etc/logrotate.d/linguaflow
/chemin/vers/linguaflow/data/logs/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

## 5. Mise à jour de l'application
```bash
./scripts/backup.sh           # 1. sauvegarder
python3 -m pip install -r requirements.txt --upgrade
# redémarrer l'application
```

## 6. Vérification de l'intégrité
```bash
python3 -m pytest tests/ -q   # suite de tests
python3 -c "from app.main import app; print('OK', app.title)"
```
