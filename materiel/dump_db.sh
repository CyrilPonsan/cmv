#!/bin/bash
WATCH_DIR="/home/admin/"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

docker exec db_gateway pg_dumpall -U "postgres" | gzip > "$WATCH_DIR/.tmp_backup_$DATE.sql.gz"
mv "$WATCH_DIR/.tmp_backup_$DATE.sql.gz" "$WATCH_DIR/all_databases_$DATE.sql.gz"

# Nettoyage des vieux dumps locaux
find "$WATCH_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete