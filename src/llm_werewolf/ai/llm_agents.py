"""LLM-based agents for the Werewolf game."""

from typing import Any

from llm_werewolf.ai.base_agent import BaseAgent
from llm_werewolf.config.llm_config import LLMProviderConfig


class OpenAIAgent(BaseAgent):
    """Agent that uses OpenAI's API (GPT models)."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the OpenAI agent.

        Args:
            model_name: Name of the OpenAI model to use.
            api_key: OpenAI API key. If None, will try to get from config.
            base_url: Base URL for OpenAI API. If None, uses default.
            temperature: Temperature for response generation.
            max_tokens: Maximum tokens in response.
        """
        super().__init__(model_name=model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Get config if not provided
        if api_key is None:
            config = LLMProviderConfig()
            provider_config = config.get_provider_config("openai")
            self.api_key = provider_config.get("api_key")
            self.base_url = provider_config.get("base_url")
        else:
            self.api_key = api_key
            self.base_url = base_url or "https://api.openai.com/v1"

        self.client: Any = None

    def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError as e:
            msg = "openai package not installed. Install with: pip install openai"
            raise ImportError(msg) from e

    def get_response(self, message: str) -> str:
        """Get response from OpenAI.

        Args:
            message: The input message/prompt.

        Returns:
            str: The AI's response.
        """
        if self.client is None:
            self.initialize()

        # Add message to history
        self.add_to_history("user", message)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            assistant_message = response.choices[0].message.content or ""
            self.add_to_history("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            error_msg = f"OpenAI API error: {e}"
            return error_msg


class AnthropicAgent(BaseAgent):
    """Agent that uses Anthropic's API (Claude models)."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the Anthropic agent.

        Args:
            model_name: Name of the Claude model to use.
            api_key: Anthropic API key. If None, will try to get from config.
            base_url: Base URL for Anthropic API. If None, uses default.
            temperature: Temperature for response generation.
            max_tokens: Maximum tokens in response.
        """
        super().__init__(model_name=model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Get config if not provided
        if api_key is None:
            config = LLMProviderConfig()
            provider_config = config.get_provider_config("anthropic")
            self.api_key = provider_config.get("api_key")
            self.base_url = provider_config.get("base_url")
        else:
            self.api_key = api_key
            self.base_url = base_url or "https://api.anthropic.com"

        self.client: Any = None

    def initialize(self) -> None:
        """Initialize the Anthropic client."""
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key, base_url=self.base_url)
        except ImportError as e:
            msg = "anthropic package not installed. Install with: pip install anthropic"
            raise ImportError(msg) from e

    def get_response(self, message: str) -> str:
        """Get response from Anthropic.

        Args:
            message: The input message/prompt.

        Returns:
            str: The AI's response.
        """
        if self.client is None:
            self.initialize()

        # Add message to history
        self.add_to_history("user", message)

        try:
            # Convert history to Anthropic format (skip system messages)
            messages = [msg for msg in self.conversation_history if msg["role"] != "system"]

            response = self.client.messages.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            assistant_message = response.content[0].text if response.content else ""
            self.add_to_history("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            error_msg = f"Anthropic API error: {e}"
            return error_msg


class GenericLLMAgent(BaseAgent):
    """Generic agent for OpenAI-compatible APIs.

    This agent can be used for:
    - Local models (Ollama, LM Studio, etc.)
    - xAI (Grok)
    - Azure OpenAI
    - Custom OpenAI-compatible endpoints
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the generic LLM agent.

        Args:
            model_name: Name of the model to use.
            api_key: API key. Can be None for local models.
            base_url: Base URL for the API endpoint.
            temperature: Temperature for response generation.
            max_tokens: Maximum tokens in response.
        """
        super().__init__(model_name=model_name)
        self.api_key = api_key or "not-needed"
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client: Any = None

    def initialize(self) -> None:
        """Initialize the OpenAI-compatible client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError as e:
            msg = "openai package not installed. Install with: pip install openai"
            raise ImportError(msg) from e

    def get_response(self, message: str) -> str:
        """Get response from the LLM.

        Args:
            message: The input message/prompt.

        Returns:
            str: The AI's response.
        """
        if self.client is None:
            self.initialize()

        # Add message to history
        self.add_to_history("user", message)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            assistant_message = response.choices[0].message.content or ""
            self.add_to_history("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            error_msg = f"LLM API error: {e}"
            return error_msg


def create_agent_from_config(
    provider: str, model_name: str | None = None, temperature: float = 0.7, max_tokens: int = 500
) -> BaseAgent:
    """Create an agent from LLM provider configuration.

    Args:
        provider: Provider name (openai, anthropic, local, xai, azure, custom).
        model_name: Model name to use. If None, uses default from config.
        temperature: Temperature for response generation.
        max_tokens: Maximum tokens in response.

    Returns:
        BaseAgent: The created agent instance.

    Raises:
        ValueError: If provider is not supported or not configured.
    """
    config = LLMProviderConfig()

    if not config.has_provider(provider):
        available = config.list_available_providers()
        msg = f"Provider '{provider}' not configured. Available: {available}"
        raise ValueError(msg)

    provider_config = config.get_provider_config(provider)
    api_key = provider_config.get("api_key")
    base_url = provider_config.get("base_url")
    default_model = provider_config.get("model")

    # Use provided model name or default from config
    final_model = model_name or default_model

    if not final_model:
        msg = f"No model specified for provider '{provider}'"
        raise ValueError(msg)

    # Create appropriate agent type
    if provider == "openai":
        return OpenAIAgent(
            model_name=final_model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    if provider == "anthropic":
        return AnthropicAgent(
            model_name=final_model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    # For all other providers, use GenericLLMAgent
    return GenericLLMAgent(
        model_name=final_model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )
