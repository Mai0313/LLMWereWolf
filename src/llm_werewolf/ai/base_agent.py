from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for AI agents that control players.

    This interface allows for easy integration of different LLM models
    (OpenAI, Anthropic, local models, etc.) by implementing the get_response method.
    """

    def __init__(self, model_name: str = "unknown") -> None:
        """Initialize the base agent.

        Args:
            model_name: Name of the AI model (e.g., "gpt-4", "claude-3").
        """
        self.model_name = model_name
        self.conversation_history: list[dict[str, str]] = []

    @abstractmethod
    def get_response(self, message: str) -> str:
        """Get a response from the AI agent.

        This is the core method that must be implemented by all agents.
        It takes a message string as input and returns a response string.

        Args:
            message: The input message/prompt for the AI.

        Returns:
            str: The AI's response.
        """
        pass

    def initialize(self) -> None:
        """Initialize the agent.

        This method can be overridden to perform any setup needed
        before the game starts (e.g., loading models, setting up connections).

        Base implementation does nothing.
        """
        # Base implementation does nothing
        return

    def reset(self) -> None:
        """Reset the agent's state.

        This method clears the conversation history and any internal state.
        Useful for starting a new game with the same agent.
        """
        self.conversation_history.clear()

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: The role of the message sender (e.g., "system", "user", "assistant").
            content: The message content.
        """
        self.conversation_history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """Get the conversation history.

        Returns:
            list[dict[str, str]]: The conversation history.
        """
        return self.conversation_history.copy()

    def __repr__(self) -> str:
        """Repr of the agent.

        Returns:
            str: Agent representation.
        """
        return f"{self.__class__.__name__}(model={self.model_name})"


class DemoAgent(BaseAgent):
    """A simple demo agent that uses random choices.

    This agent is for testing and demonstration purposes.
    It doesn't use any actual AI model.
    """

    def __init__(self) -> None:
        """Initialize the demo agent."""
        super().__init__(model_name="demo-random")

    def get_response(self, message: str) -> str:
        """Get a simple response.

        This implementation just returns a simple acknowledgment.
        In a real implementation, this would call an LLM API.

        Args:
            message: The input message.

        Returns:
            str: A simple response.
        """
        import random

        # Simple responses for demo
        responses = [
            "I agree.",
            "I'm not sure about that.",
            "Let me think about it.",
            "That's interesting.",
            "I have my suspicions.",
        ]

        return random.choice(responses)  # noqa: S311


class HumanAgent(BaseAgent):
    """Agent for human players (console input).

    This agent prompts for human input via the console.
    """

    def __init__(self) -> None:
        """Initialize the human agent."""
        super().__init__(model_name="human")
        from rich.console import Console

        self.console = Console()

    def get_response(self, message: str) -> str:
        """Get response from human input.

        Args:
            message: The prompt message.

        Returns:
            str: Human's response.
        """
        self.console.print(f"\n{message}")
        return input("Your response: ")
