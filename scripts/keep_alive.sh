#!/bin/bash
# Script for Streamlit active 24/7

PROJECT_DIR="/home/ubuntu/GitHubProject"  
LOG_FILE="$PROJECT_DIR/logs/streamlit.log"
PID_FILE="$PROJECT_DIR/streamlit.pid"

cd "$PROJECT_DIR"

# Function to check Streamlit is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Process is running
        fi
    fi
    return 1  # Process is not running
}

# Fonction to start Streamlit
start_streamlit() {
    echo "Starting Streamlit at $(date)" >> "$LOG_FILE"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # kill other instances
    pkill -f "streamlit run app.py" 2>/dev/null
    
    # start Streamlit in background
    nohup streamlit run app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.runOnSave true \
        >> "$LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    echo "Streamlit started with PID $(cat $PID_FILE)" >> "$LOG_FILE"
}

# Function to stop Streamlit
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

# Function to restart Streamlit
restart_streamlit() {
    echo "Restarting Streamlit at $(date)" >> "$LOG_FILE"
    stop_streamlit
    sleep 2
    start_streamlit
}

# Parse arguments
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
        
        if ! is_running; then
            echo "Streamlit not running, starting..." >> "$LOG_FILE"
            start_streamlit
        fi
        ;;
esac
