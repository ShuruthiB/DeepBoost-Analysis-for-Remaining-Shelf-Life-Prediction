"""SpoilSense AI desktop launcher: starts the API + bundled UI and opens the browser."""
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def _data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    path = Path(root) / "SpoilSenseAI"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _free_port(preferred: int = 8000) -> int:
    for port in (preferred, 0):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return sock.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("No free port available")


def main() -> None:
    # Keep the database somewhere writable (the bundle itself is read-only/temporary).
    os.environ.setdefault("DEEPBOOST_DATABASE_PATH", str(_data_dir() / "inventory.sqlite3"))

    import uvicorn
    from backend.main import app  # imported after the env var is set

    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    threading.Thread(
        target=lambda: (time.sleep(2.5), webbrowser.open(url)), daemon=True
    ).start()
    print(f"SpoilSense AI running at {url}  (close this window to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
