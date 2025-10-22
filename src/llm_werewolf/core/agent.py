import random

from pydantic import Field, BaseModel
from rich.console import Console

console = Console()


class BaseAgent(BaseModel):
    """Base class for all agents.

    All agents must implement get_response() method.
    Provides shared functionality like __repr__.
    """

    name: str
    model: str

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

    def add_decision(self, decision: str) -> None:
        """Add a decision to the decision history.

        Default implementation does nothing (for non-LLM agents).

        Args:
            decision: A safe summary of the decision.
        """
        pass

    def get_decision_context(self) -> str:
        """Get a formatted string of decision history for context.

        Default implementation returns empty string (for non-LLM agents).

        Returns:
            str: Formatted decision history.
        """
        return ""

    def __repr__(self) -> str:
        """Return a string representation of the agent.

        Returns:
            str: The agent name and model.
        """
        return f"{self.name} ({self.model})"


class DemoAgent(BaseAgent):
    """Demo agent that returns random canned responses.

    Useful for testing game logic without requiring AI API calls.
    """

    model: str = Field(default="demo")

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

    model: str = Field(default="human")

    def get_response(self, message: str) -> str:
        """Get response from human input.

        Args:
            message: The prompt message.

        Returns:
            str: The user's input.
        """
        console.print(f"\n{message}")
        return input("Your response: ")
