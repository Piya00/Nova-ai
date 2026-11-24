import threading
import time
import sys
import uvicorn
import webview
import socket
import uuid
import os
from pathlib import Path
from server.app import app  # Importing the FastAPI instance from server/app.py

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    # Run the existing FastAPI app
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="error")

def generate_launch_id():
    """Generate a unique application launch ID"""
    launch_dir = Path.home() / ".nova_launch_ids"
    launch_dir.mkdir(exist_ok=True)

    launch_id_file = launch_dir / "current_launch_id"

    if launch_id_file.exists():
        try:
            with open(launch_id_file, 'r') as f:
                return f.read().strip()
        except:
            pass

    # Generate new launch ID
    new_launch_id = str(uuid.uuid4())

    try:
        with open(launch_id_file, 'w') as f:
            f.write(new_launch_id)
    except:
        pass

    return new_launch_id

if __name__ == '__main__':
    PORT = 7860

    if is_port_in_use(PORT):
        print(f"Error: Port {PORT} is already in use.")
        print("Please close any other instances of Nova or applications using this port.")
        sys.exit(1)

    # Generate application launch ID
    app_launch_id = generate_launch_id()
    os.environ['NOVA_APP_LAUNCH_ID'] = app_launch_id

    # Start backend in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    print(f"Waiting for Nova server to start... (Launch ID: {app_launch_id})")
    max_retries = 10
    for _ in range(max_retries):
        if is_port_in_use(PORT):
            break
        time.sleep(0.5)
    else:
        print("Error: Could not connect to the Nova server.")
        sys.exit(1)

    print("Server ready. Launching desktop window...")

    # Create the window
    window = webview.create_window(
        'NovaAI Companion',
        f'http://127.0.0.1:7860?launch_id={app_launch_id}',
        width=1200,
        height=800
    )

    # Start webview (this blocks until the window is closed)
    webview.start()

    print("Desktop application closed.")
    sys.exit(0)
