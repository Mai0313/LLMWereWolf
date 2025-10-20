"""Base Agent and Implementations.

This module defines the base agent class and provides implementations
for human and demo agents. This keeps the core game logic independent of AI.
"""

import random

from pydantic import Field, BaseModel
from rich.console import Console

console = Console()


# ============================================================================
# Base Agent Class
# ============================================================================


class BaseAgent(BaseModel):
    """Base class for all agents.

    All agents must implement get_response() method.
    Provides shared functionality like __repr__.
    """

    model_name: str

    def get_response(self, message: str) -> str:
        """Get a response from the agent.

        Args:
            message: The prompt message.

        Returns:
            str: The agent's response.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement get_response()")

    def __repr__(self) -> str:
        """Return a string representation of the agent.

        Returns:
            str: The model name.
        """
        return self.model_name


# ============================================================================
# Agent Implementations
# ============================================================================


class DemoAgent(BaseAgent):
    """Demo agent that returns random canned responses.

    Useful for testing game logic without requiring AI API calls.
    """

    model_name: str = Field(default="demo")

    def get_response(self, message: str) -> str:
        """Return a canned response.

        Args:
            message: The prompt message (ignored).

        Returns:
            str: A random canned response.
        """
        responses = [
            "I agree.",
            "I'm not sure about that.",
            "Let me think about it.",
            "That's interesting.",
            "I have my suspicions.",
        ]
        return random.choice(responses)  # noqa: S311


class HumanAgent(BaseAgent):
    """Human agent that prompts for console input.

    Allows human players to participate in the game via terminal input.
    """

    model_name: str = Field(default="human")

    def get_response(self, message: str) -> str:
        """Get response from human input.

        Args:
            message: The prompt message.

        Returns:
            str: Human's response from console input.
        """
        console.print(f"\n{message}")
        return input("Your response: ")
