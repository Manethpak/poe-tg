#!/usr/bin/env python3
"""
Development script that watches for file changes and automatically restarts the bot.
"""
import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class BotRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_pending = False

    def on_modified(self, event):
        if event.is_directory:
            return

        # Convert to string and only watch Python files
        src_path = str(event.src_path)
        if not src_path.endswith(".py"):
            return

        # Ignore __pycache__ and .pyc files
        if "__pycache__" in src_path or src_path.endswith(".pyc"):
            return

        print(f"\n🔄 File changed: {src_path}")
        self.restart_bot()

    def restart_bot(self):
        if self.restart_pending:
            return

        self.restart_pending = True
        print("🔄 Restarting bot...")

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Start the bot in a new process
        self.start_bot()
        self.restart_pending = False

    def start_bot(self):
        try:
            self.process = subprocess.Popen([sys.executable, "main.py", "--poll"])
            print("✅ Bot started successfully")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")


def main():
    print("🚀 Starting Poe Telegram Bot in development mode...")
    print("📁 Watching for file changes...")
    print("🛑 Press Ctrl+C to stop")

    handler = BotRestartHandler()
    observer = Observer()

    # Watch the poe_tg directory for changes
    observer.schedule(handler, path="poe_tg", recursive=True)
    observer.start()

    # Start the bot initially
    handler.start_bot()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
        if handler.process:
            handler.process.terminate()
            handler.process.wait()
        observer.stop()
        observer.join()
        print("✅ Development server stopped")


if __name__ == "__main__":
    main()
