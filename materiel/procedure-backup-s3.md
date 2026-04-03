# Procédure de mise en place des backups et upload S3

## Prérequis

- Accès root ou sudo sur le serveur
- Docker installé et les containers FastAPI en cours d'exécution
- Python 3 avec pip
- Un rôle IAM attaché à l'instance EC2 avec les permissions S3 nécessaires (`s3:PutObject`, `s3:GetObject`, `s3:HeadBucket`)

---

## 1. Copier les scripts sur le serveur

```bash
# Créer le répertoire de travail
sudo mkdir -p /opt/s3-upload

# Copier les scripts
sudo cp materiel/dump_db.sh /opt/s3-upload/
sudo cp materiel/db-backup.sh /opt/s3-upload/
sudo cp materiel/s3_upload.py /opt/s3-upload/

# Rendre les scripts exécutables
sudo chmod +x /opt/s3-upload/dump_db.sh
sudo chmod +x /opt/s3-upload/db-backup.sh
```

---

## 2. Installer les dépendances Python

```bash
sudo pip3 install boto3 watchdog
```

---

## 3. Configurer le fichier config.ini

```bash
sudo mkdir -p /etc/s3-upload
sudo nano /etc/s3-upload/config.ini
```

Contenu du fichier :

```ini
[S3]
bucket_name = nom-du-bucket-principal

[S3_BACKUP]
bucket_name = nom-du-bucket-secondaire
region = eu-west-3

[LOCAL]
folder_to_watch = /home/admin/
```

> `folder_to_watch` doit correspondre au `WATCH_DIR` défini dans `dump_db.sh` et `db-backup.sh` (par défaut `/home/admin/`).

---

## 4. Créer le service systemd pour s3-upload

```bash
sudo nano /etc/systemd/system/s3-upload.service
```

Contenu :

```ini
[Unit]
Description=S3 Upload - Surveillance et upload automatique vers S3
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/s3-upload/s3_upload.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Activer et démarrer le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable s3-upload.service
sudo systemctl start s3-upload.service
```

Vérifier le statut :

```bash
sudo systemctl status s3-upload.service
sudo journalctl -u s3-upload.service -f
```

---

## 5. Configurer le cron pour les backups à 3h du matin

```bash
sudo crontab -e
```

Ajouter les lignes suivantes :

```cron
# Dump des bases de données PostgreSQL - tous les jours à 3h00
0 3 * * * /opt/s3-upload/dump_db.sh >> /var/log/dump_db.log 2>&1

# Récupération des logs FastAPI - tous les jours à 3h05
5 3 * * * /opt/s3-upload/db-backup.sh >> /var/log/db-backup.log 2>&1
```

> Le script `db-backup.sh` est décalé de 5 minutes pour éviter un conflit de charge avec le dump DB.

---

## 6. Vérification

```bash
# Vérifier que le cron est bien enregistré
sudo crontab -l

# Vérifier que le service s3-upload tourne
sudo systemctl status s3-upload.service

# Vérifier les logs du service
sudo journalctl -u s3-upload.service --since today

# Tester manuellement les scripts
sudo /opt/s3-upload/dump_db.sh
sudo /opt/s3-upload/db-backup.sh
```

---

## Résumé du flux

```
3h00  →  dump_db.sh        →  dump SQL compressé dans /home/admin/
3h05  →  db-backup.sh      →  archive logs FastAPI dans /home/admin/
         s3-upload.service  →  détecte les nouveaux fichiers et les upload vers S3
```
