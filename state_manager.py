# state_manager.py

import json
from typing import Any, Dict

class StateManager:
    """
    Manages the shared state (JSON-like dictionary) between all agents.
    """

    def __init__(self):
        self.state: Dict[str, Any] = {
            "pdf_text": None,
            "chapters": [],
            "slides": [],
            "design": {},
            "media": [],
            "output_path": None
        }

    def update(self, key: str, value: Any):
        """Update a specific key in the shared state."""
        self.state[key] = value

    def get(self, key: str):
        """Retrieve a value by key."""
        return self.state.get(key, None)

    def save(self, path: str = "shared_state.json"):
        """Save current state to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4)

    def load(self, path: str = "shared_state.json"):
        """Load state from an existing JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            self.state = json.load(f)
            
    def append_log(self, message: str):
        self.state.setdefault("log", [])
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state["log"].append(f"[{ts}] {message}")


# Quick test
if __name__ == "__main__":
    sm = StateManager()
    sm.update("pdf_text", "Sample syllabus text from chapter 1.")
    sm.save()
    print("✅ State saved successfully!")
