"""Game engine module for LLM Werewolf.

This module provides the core game engine functionality split across multiple files:
- base.py: Core game engine initialization and main loop
- night_phase.py: Night phase execution logic
- day_phase.py: Day discussion phase logic
- voting_phase.py: Voting phase logic
- death_handler.py: Death-related logic (kills, lover deaths, etc.)
- action_processor.py: Action processing logic

The GameEngine class combines all these components using mixins.
"""

from llm_werewolf.core.engine.game_engine import GameEngine

__all__ = ["GameEngine"]
