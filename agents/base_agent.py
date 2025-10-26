# agents/base_agent.py

from abc import ABC, abstractmethod 
#ABC defines BaseAgent as an abstract blueprint that can’t be instantiated directly, while @abstractmethod enforces implementation in subclasses—ensuring all specialized agents (Content, Format, etc.) follow a common structure.
from datetime import datetime
#Used for timestamping log messages, making it easier to track the sequence and timing of agent actions during debugging.
from typing import Any
# from typing import Any imports the Any type hint from Python’s typing module — it’s used to indicate that a variable, parameter, or return value can be of any type

class BaseAgent(ABC): # It ensures they all share common functionalitiesh
    """
    Base class for all agents. Provides logging, state management, and structure.
    """

    def __init__(self, name: str, state_manager): # Defines the constructor method. This method runs automatically whenever a new agent object is created
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
