# Configuration
PROJECT_DIR="/home/ubuntu/project"  
DATE=$(date +"%Y-%m-%d")
REPORT_DIR="$PROJECT_DIR/reports"
LOG_FILE="$REPORT_DIR/daily_report_$DATE.txt"

# Create file if it doesn't exist
mkdir -p "$REPORT_DIR"


echo "========================================" > "$LOG_FILE"
echo "DAILY AUTOMATED REPORT" >> "$LOG_FILE"
echo "Date: $DATE" >> "$LOG_FILE"
echo "Time: $(date +"%H:%M:%S")" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Activate virtual environment
cd "$PROJECT_DIR"
source venv/bin/activate

# Execute Python script
python3 scripts/generate_report.py ENGI.PA ENGIE >> "$LOG_FILE" 2>&1

# Execution status
if [ $? -eq 0 ]; then
    echo "" >> "$LOG_FILE"
    echo "✅ Report generated successfully at $(date +"%H:%M:%S")" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "❌ Error generating report at $(date +"%H:%M:%S")" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"



# Clean old reports
find "$REPORT_DIR" -name "daily_report_*.txt" -mtime +30 -delete

# Log
echo "Daily report script executed at $(date)" >> "$PROJECT_DIR/logs/cron.log"
