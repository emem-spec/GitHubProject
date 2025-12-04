#!/bin/bash
# Script pour maintenir Streamlit actif 24/7

PROJECT_DIR="/home/ubuntu/project"  # Adapter selon votre chemin
LOG_FILE="$PROJECT_DIR/logs/streamlit.log"
PID_FILE="$PROJECT_DIR/streamlit.pid"

cd "$PROJECT_DIR"

# Fonction pour vérifier si Streamlit tourne
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Process is running
        fi
    fi
    return 1  # Process is not running
}

# Fonction pour démarrer Streamlit
start_streamlit() {
    echo "Starting Streamlit at $(date)" >> "$LOG_FILE"
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Tuer les anciennes instances
    pkill -f "streamlit run app.py" 2>/dev/null
    
    # Démarrer Streamlit en arrière-plan
    nohup streamlit run app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.runOnSave true \
        >> "$LOG_FILE" 2>&1 &
    
    # Sauvegarder le PID
    echo $! > "$PID_FILE"
    
    echo "Streamlit started with PID $(cat $PID_FILE)" >> "$LOG_FILE"
}

# Fonction pour arrêter Streamlit
stop_streamlit() {
    echo "Stopping Streamlit at $(date)" >> "$LOG_FILE"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null
        rm "$PID_FILE"
    fi
    
    pkill -f "streamlit run app.py" 2>/dev/null
    echo "Streamlit stopped" >> "$LOG_FILE"
}

# Fonction pour redémarrer Streamlit
restart_streamlit() {
    echo "Restarting Streamlit at $(date)" >> "$LOG_FILE"
    stop_streamlit
    sleep 2
    start_streamlit
}

# Parser les arguments
case "$1" in
    start)
        if is_running; then
            echo "Streamlit is already running"
        else
            start_streamlit
        fi
        ;;
    stop)
        stop_streamlit
        ;;
    restart)
        restart_streamlit
        ;;
    status)
        if is_running; then
            echo "Streamlit is running (PID: $(cat $PID_FILE))"
        else
            echo "Streamlit is not running"
        fi
        ;;
    *)
        # Par défaut, vérifier et redémarrer si nécessaire
        if ! is_running; then
            echo "Streamlit not running, starting..." >> "$LOG_FILE"
            start_streamlit
        fi
        ;;
esac
