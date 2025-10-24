import os
import random
from functools import cached_property

import dotenv
from openai import OpenAI
from pydantic import Field, BaseModel, ConfigDict, computed_field
from rich.console import Console
from openai.types.shared import ReasoningEffort

from llm_werewolf.core.config import PlayerConfig

dotenv.load_dotenv()


console = Console()


class BaseAgent(BaseModel):
    """Base class for all agents.

    All agents must implement get_response() method.
    Provides shared functionality like __repr__.
    """

    name: str = Field(
        ...,
        title="The Name of the player",
        description="Display name for the player",
        examples=["AI-GPT-5"],
    )
    model: str = Field(
        ...,
        title="Model Name",
        description="The model name of your player",
        examples=["gpt-5", "human", "demo"],
    )

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
        """Return a canned response based on message type.

        Args:
            message: The prompt message.

        Returns:
            str: An appropriate response based on the message type.
        """
        # Check if it's a yes/no question
        if "ONLY 'YES' or 'NO'" in message or "respond with ONLY 'YES' or 'NO'" in message:
            # For sheriff campaign, use 30% chance to say YES (creates 2-3 candidates in 12 players)
            if "campaign for sheriff" in message.lower():
                return "YES" if random.random() < 0.3 else "NO"  # noqa: S311
            # For other yes/no questions, 50/50
            return random.choice(["YES", "NO"])  # noqa: S311

        # Check if it's a target selection question (contains numbered list)
        if "responding with ONLY the number" in message or "select a target" in message.lower():
            # Extract available numbers from the message
            import re

            # Find all lines that look like "1. PlayerName"
            lines = message.split("\n")
            max_number = 0
            for line in lines:
                match = re.match(r"^\s*(\d+)\.\s+", line)
                if match:
                    max_number = max(max_number, int(match.group(1)))

            if max_number > 0:
                # Randomly select a number
                return str(random.randint(1, max_number))  # noqa: S311

        # For campaign speeches and free-form responses
        if "campaign speech" in message.lower():
            speeches = [
                "I believe I can be a good sheriff. Trust me, I'm on the villagers' side!",
                "Vote for me and I'll use my power wisely to protect the village.",
                "I promise to lead us to victory. Let me be your sheriff!",
                "I have good instincts about who the werewolves are. Give me your vote!",
            ]
            return random.choice(speeches)  # noqa: S311

        # Default canned responses
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


class LLMAgent(BaseAgent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    base_url: str
    reasoning_effort: ReasoningEffort | None = Field(default=None)
    language: str = Field(...)
    chat_history: list[dict[str, str]] = Field(default=[])
    decision_history: list[str] = Field(default=[])

    @computed_field
    @cached_property
    def client(self) -> OpenAI:
        """Create and cache OpenAI client instance.

        Returns:
            OpenAI: Cached OpenAI client instance.
        """
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_response(self, message: str) -> str:
        """Get a response from the LLM.

        Args:
            message: The prompt message.

        Returns:
            str: The complete response from the LLM.
        """
        message += f"\nPlease respond in {self.language}."
        self.chat_history.append({"role": "user", "content": message})

        if self.reasoning_effort:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                reasoning_effort=self.reasoning_effort,
                stream=False,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model, messages=self.chat_history, stream=False
            )

        full_response = response.choices[0].message.content or ""
        self.chat_history.append({"role": "assistant", "content": full_response})
        return full_response

    def add_decision(self, decision: str) -> None:
        """Add a decision to the decision history.

        This records WHAT the agent decided without sensitive context.

        Args:
            decision: A safe summary of the decision (e.g., "Round 1: Checked Bob, result: villager")
        """
        self.decision_history.append(decision)

    def get_decision_context(self) -> str:
        """Get a formatted string of decision history for context.

        Returns:
            str: Formatted decision history without sensitive information.
        """
        if not self.decision_history:
            return ""
        return "\n\nYour previous actions:\n" + "\n".join(f"- {d}" for d in self.decision_history)


def create_agent(
    config: PlayerConfig, language: str = "en-US"
) -> DemoAgent | HumanAgent | LLMAgent:
    """Create an agent instance from player configuration.

    Args:
        config: Player configuration.
        language: Language code for the agent (e.g., "en-US", "zh-TW").

    Returns:
        DemoAgent | HumanAgent | LLMAgent: Created agent instance.

    Raises:
        ValueError: If configuration is invalid or API key is missing.
    """
    model = config.model.lower()

    if model == "human":
        return HumanAgent(name=config.name, model="human")

    if model == "demo":
        return DemoAgent(name=config.name, model="demo")

    api_key = None
    if config.api_key_env:
        api_key = os.getenv(config.api_key_env)
    if not api_key:
        raise ValueError(
            f"API key not found in environment variable '{config.api_key_env}' for player '{config.name}'"
        )

    return LLMAgent(
        name=config.name,
        model=config.model,
        api_key=api_key,
        base_url=config.base_url,
        language=language,
    )
