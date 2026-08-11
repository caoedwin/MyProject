#!/bin/bash
# ============================================================
# MyProject 数据库与媒体文件备份脚本
# 建议通过 cron 每天凌晨执行:
#   0 2 * * * /opt/MyProject/deploymentprepare/backup.sh
# ============================================================

set -e

BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/MyProject"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="myproject"
DB_USER="myproject_user"
DB_PASS="CHANGE_ME_STRONG_PASSWORD"
KEEP_DAYS=30

mkdir -p "$BACKUP_DIR"

# ---------- 数据库备份 ----------
echo "备份数据库 $DB_NAME ..."
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    > "$BACKUP_DIR/db_${DATE}.sql"

# ---------- 媒体文件备份 ----------
echo "备份媒体文件..."
tar czf "$BACKUP_DIR/media_${DATE}.tar.gz" -C "$PROJECT_DIR" media/

# ---------- 压缩并清理 ----------
cd "$BACKUP_DIR"
tar czf "myproject_full_${DATE}.tar.gz" "db_${DATE}.sql" "media_${DATE}.tar.gz"
rm -f "db_${DATE}.sql" "media_${DATE}.tar.gz"

# ---------- 删除过期备份 ----------
echo "清理 ${KEEP_DAYS} 天前的备份..."
find "$BACKUP_DIR" -name "myproject_full_*.tar.gz" -mtime +${KEEP_DAYS} -delete

echo "备份完成: myproject_full_${DATE}.tar.gz"
ls -lh "$BACKUP_DIR/"
