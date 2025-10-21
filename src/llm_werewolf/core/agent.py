import random
from collections.abc import Iterator

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

    def get_response(self, message: str) -> Iterator[str]:
        """Get a streaming response from the agent.

        Args:
            message: The prompt message.

        Yields:
            str: Chunks of the agent's response.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement get_response()")

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

    def get_response(self, message: str) -> Iterator[str]:
        """Return a canned response as a stream.

        Args:
            message: The prompt message (ignored).

        Yields:
            str: The complete response in one chunk.
        """
        responses = [
            "I agree.",
            "I'm not sure about that.",
            "Let me think about it.",
            "That's interesting.",
            "I have my suspicions.",
        ]
        yield random.choice(responses)  # noqa: S311


class HumanAgent(BaseAgent):
    """Human agent that prompts for console input.

    Allows human players to participate in the game via terminal input.
    """

    model: str = Field(default="human")

    def get_response(self, message: str) -> Iterator[str]:
        """Get response from human input as a stream.

        Args:
            message: The prompt message.

        Yields:
            str: The complete response in one chunk.
        """
        console.print(f"\n{message}")
        yield input("Your response: ")
