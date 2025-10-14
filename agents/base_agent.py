# agents/base_agent.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

class BaseAgent(ABC):
    """
    Base class for all agents. Provides logging, state management, and structure.
    """

    def __init__(self, name: str, state_manager):
        self.name = name
        self.sm = state_manager  # Shared StateManager instance

    def log(self, message: str):
        """Simple timestamped log for debugging and clarity."""
        time = datetime.now().strftime("%H:%M:%S")
        print(f"[{time}] [{self.name}] {message}")

    def update_state(self, key: str, value: Any):
        """Update a value in the shared state."""
        self.sm.update(key, value)
        self.log(f"Updated state key '{key}'")

    @abstractmethod
    def run(self):
        """
        Each agent must implement its own run() method.
        """
        pass
