
import subprocess
import threading
import time
import sys

def run_flask():
    """Run Flask server"""
    print("🌐 Starting Flask server...")
    subprocess.run([sys.executable, "main.py"])

def run_telegram_bot():
    """Run Telegram bot"""
    print("🤖 Starting Telegram bot...")
    time.sleep(3)  # Wait for Flask to start
    subprocess.run([sys.executable, "telegram_bot.py"])

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Telegram bot in main thread
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        sys.exit(0)
