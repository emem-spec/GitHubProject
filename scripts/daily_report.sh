# Configuration
PROJECT_DIR="/home/ubuntu/project"  # Adapter selon votre chemin
DATE=$(date +"%Y-%m-%d")
REPORT_DIR="$PROJECT_DIR/reports"
LOG_FILE="$REPORT_DIR/daily_report_$DATE.txt"

# Créer le dossier reports s'il n'existe pas
mkdir -p "$REPORT_DIR"

# En-tête du rapport
echo "========================================" > "$LOG_FILE"
echo "DAILY AUTOMATED REPORT" >> "$LOG_FILE"
echo "Date: $DATE" >> "$LOG_FILE"
echo "Time: $(date +"%H:%M:%S")" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Activer l'environnement virtuel
cd "$PROJECT_DIR"
source venv/bin/activate

# Exécuter le script Python de rapport
python3 scripts/generate_report.py ENGI.PA ENGIE >> "$LOG_FILE" 2>&1

# Statut de l'exécution
if [ $? -eq 0 ]; then
    echo "" >> "$LOG_FILE"
    echo "✅ Report generated successfully at $(date +"%H:%M:%S")" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "❌ Error generating report at $(date +"%H:%M:%S")" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"

# Envoyer une notification (optionnel)
# echo "Daily report generated" | mail -s "Quant Report $DATE" your@email.com

# Nettoyer les anciens rapports (garder les 30 derniers jours)
find "$REPORT_DIR" -name "daily_report_*.txt" -mtime +30 -delete

# Log
echo "Daily report script executed at $(date)" >> "$PROJECT_DIR/logs/cron.log"
