from typing import Any

from llm_werewolf.ai.base_agent import BaseAgent


class LLMAgent(BaseAgent):
    """Unified agent for all LLM providers using OpenAI ChatCompletion API.

    This agent uses the OpenAI client which supports ChatCompletion-compatible APIs
    from various providers including OpenAI, Anthropic, xAI, local models, etc.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the LLM agent.

        Args:
            model_name: Name of the model to use (e.g., "gpt-4", "claude-3-5-sonnet").
            api_key: API key for the provider. Can be None for local models.
            base_url: Base URL for the API endpoint. Required for non-OpenAI providers.
            temperature: Temperature for response generation (0.0-2.0).
            max_tokens: Maximum tokens in response.
        """
        super().__init__(model_name=model_name)
        self.api_key = api_key or "not-needed"
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client: Any = None

    def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError as e:
            msg = "openai package not installed. Install with: uv sync --group llm-openai"
            raise ImportError(msg) from e

    def get_response(self, message: str) -> str:
        """Get response from the LLM using ChatCompletion API.

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
