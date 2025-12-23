"""
Personality Integration Manager
Manages personality system imports to avoid circular dependencies
"""

from typing import Optional, Any, Dict
import importlib


class PersonalityManager:
    """Lazy-loading manager for personality system components"""

    _personality_integration = None
    _world_cropper = None
    _personality_adapter = None

    @classmethod
    def get_personality_integration(cls, enable: bool = False):
        """Get personality integration with lazy loading"""
        if not enable:
            return None

        if cls._personality_integration is None:
            try:
                mod = importlib.import_module('llm_werewolf.core.engine.personality_integration')
                cls._personality_integration = mod.PersonalityEngineIntegration(enable_personality_system=True)
            except ImportError as e:
                print(f"Warning: Could not load personality integration: {e}")
                return None

        return cls._personality_integration

    @classmethod
    def get_world_cropper(cls):
        """Get world cropper with lazy loading"""
        if cls._world_cropper is None:
            try:
                mod = importlib.import_module('llm_werewolf.core.observation.world_cropper')
                cls._world_cropper = mod.WorldCropper()
            except ImportError as e:
                print(f"Warning: Could not load world cropper: {e}")
                return None

        return cls._world_cropper

    @classmethod
    def get_personality_adapter(cls):
        """Get personality adapter with lazy loading"""
        if cls._personality_adapter is None:
            try:
                mod = importlib.import_module('llm_werewolf.core.agents.personality_adapter')
                cls._personality_adapter = mod.PersonalityAdapter()
            except ImportError as e:
                print(f"Warning: Could not load personality adapter: {e}")
                return None

        return cls._personality_adapter

    @classmethod
    def is_available(cls) -> bool:
        """Check if personality system is available"""
        try:
            importlib.import_module('llm_werewolf.core.personality.models')
            importlib.import_module('llm_werewolf.core.observation.player_view')
            importlib.import_module('llm_werewolf.core.decision.models')
            return True
        except ImportError:
            return False