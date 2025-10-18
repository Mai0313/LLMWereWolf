"""LLM configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderConfig(BaseSettings):
    """Configuration for a specific LLM provider."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    # OpenAI
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")

    # Anthropic
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_base_url: str = Field(
        default="https://api.anthropic.com", alias="ANTHROPIC_BASE_URL"
    )
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", alias="ANTHROPIC_MODEL")

    # Google Gemini
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_base_url: str = Field(
        default="https://generativelanguage.googleapis.com", alias="GEMINI_BASE_URL"
    )
    gemini_model: str = Field(default="gemini-pro", alias="GEMINI_MODEL")

    # xAI
    xai_api_key: str | None = Field(default=None, alias="XAI_API_KEY")
    xai_base_url: str = Field(default="https://api.x.ai/v1", alias="XAI_BASE_URL")
    xai_model: str = Field(default="grok-beta", alias="XAI_MODEL")

    # Local models (Ollama, etc.)
    local_base_url: str = Field(default="http://localhost:11434", alias="LOCAL_BASE_URL")
    local_model: str = Field(default="llama2", alias="LOCAL_MODEL")

    # Azure OpenAI
    azure_api_key: str | None = Field(default=None, alias="AZURE_API_KEY")
    azure_endpoint: str | None = Field(default=None, alias="AZURE_ENDPOINT")
    azure_deployment: str | None = Field(default=None, alias="AZURE_DEPLOYMENT")
    azure_api_version: str = Field(default="2024-02-15-preview", alias="AZURE_API_VERSION")

    # Generic/Custom provider
    custom_api_key: str | None = Field(default=None, alias="CUSTOM_API_KEY")
    custom_base_url: str | None = Field(default=None, alias="CUSTOM_BASE_URL")
    custom_model: str | None = Field(default=None, alias="CUSTOM_MODEL")

    def get_provider_config(self, provider: str) -> dict[str, str | None]:
        """Get configuration for a specific provider.

        Args:
            provider: The provider name (openai, anthropic, gemini, xai, local, azure, custom).

        Returns:
            dict containing api_key, base_url, and model for the provider.

        Raises:
            ValueError: If provider is not recognized.
        """
        provider = provider.lower()

        configs = {
            "openai": {
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url,
                "model": self.openai_model,
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "base_url": self.anthropic_base_url,
                "model": self.anthropic_model,
            },
            "gemini": {
                "api_key": self.gemini_api_key,
                "base_url": self.gemini_base_url,
                "model": self.gemini_model,
            },
            "xai": {
                "api_key": self.xai_api_key,
                "base_url": self.xai_base_url,
                "model": self.xai_model,
            },
            "local": {
                "api_key": None,  # Local models typically don't need API key
                "base_url": self.local_base_url,
                "model": self.local_model,
            },
            "azure": {
                "api_key": self.azure_api_key,
                "base_url": self.azure_endpoint,
                "model": self.azure_deployment,
                "api_version": self.azure_api_version,
            },
            "custom": {
                "api_key": self.custom_api_key,
                "base_url": self.custom_base_url,
                "model": self.custom_model,
            },
        }

        if provider not in configs:
            available = ", ".join(configs.keys())
            msg = f"Unknown provider '{provider}'. Available: {available}"
            raise ValueError(msg)

        return configs[provider]

    def has_provider(self, provider: str) -> bool:
        """Check if a provider is configured (has API key).

        Args:
            provider: The provider name.

        Returns:
            bool: True if provider has API key configured.
        """
        try:
            config = self.get_provider_config(provider)
            # Local provider doesn't need API key
            if provider.lower() == "local":
                return True
            return config.get("api_key") is not None
        except ValueError:
            return False

    def list_available_providers(self) -> list[str]:
        """List all configured providers.

        Returns:
            list[str]: Names of providers with API keys configured.
        """
        providers = ["openai", "anthropic", "gemini", "xai", "local", "azure", "custom"]
        return [p for p in providers if self.has_provider(p)]


# Global config instance
_config_instance: LLMProviderConfig | None = None


def get_llm_config() -> LLMProviderConfig:
    """Get the global LLM configuration instance.

    Returns:
        LLMProviderConfig: The configuration instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = LLMProviderConfig()
    return _config_instance


def reload_llm_config() -> LLMProviderConfig:
    """Reload the LLM configuration from environment.

    Returns:
        LLMProviderConfig: The new configuration instance.
    """
    global _config_instance
    _config_instance = LLMProviderConfig()
    return _config_instance
