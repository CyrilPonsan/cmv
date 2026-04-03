#!/bin/bash
# -------------------------------------------------------
# Récupération et compression des logs FastAPI les plus
# récents (fastapi-efk.log.2026*) depuis les 4 containers
# -------------------------------------------------------

WATCH_DIR="/home/admin/backups"
DATE=$(date +%Y%m%d_%H%M%S)
TMP_DIR=$(mktemp -d)

# Créer le répertoire de destination s'il n'existe pas
mkdir -p "$WATCH_DIR"
ARCHIVE_NAME="fastapi-logs_${DATE}.tar.gz"

# Container => chemin des logs dans le container
declare -A CONTAINERS=(
  ["cmv_gateway"]="/app/app/logs"
  ["cmv_patients"]="/app/app/logs"
  ["cmv_chambres"]="/app/app/logs"
  ["cmv_ml"]="/code/app/logs"
)

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

for CONTAINER in "${!CONTAINERS[@]}"; do
  LOG_DIR="${CONTAINERS[$CONTAINER]}"

  # Trouver le fichier le plus récent qui commence par fastapi-efk.log.2026
  LATEST_FILE=$(docker exec "$CONTAINER" bash -c \
    "ls -t ${LOG_DIR}/fastapi-efk.log.2026* 2>/dev/null | head -1")

  if [ -z "$LATEST_FILE" ]; then
    echo "[WARN] Aucun fichier fastapi-efk.log.2026* trouvé dans $CONTAINER"
    continue
  fi

  FILENAME=$(basename "$LATEST_FILE")
  DEST="${TMP_DIR}/${CONTAINER}_${FILENAME}"

  echo "[INFO] $CONTAINER : récupération de $LATEST_FILE"
  docker cp "${CONTAINER}:${LATEST_FILE}" "$DEST"

  if [ $? -ne 0 ]; then
    echo "[ERROR] Échec de la copie depuis $CONTAINER"
  fi
done

# Vérifier qu'on a récupéré au moins un fichier
FILE_COUNT=$(ls -1 "$TMP_DIR" 2>/dev/null | wc -l)
if [ "$FILE_COUNT" -eq 0 ]; then
  echo "[ERROR] Aucun fichier log récupéré, abandon."
  exit 1
fi

# Compression et copie dans WATCH_DIR
tar -czf "${WATCH_DIR}/${ARCHIVE_NAME}" -C "$TMP_DIR" .

echo "[OK] Archive créée : ${WATCH_DIR}/${ARCHIVE_NAME} ($FILE_COUNT fichier(s))"
