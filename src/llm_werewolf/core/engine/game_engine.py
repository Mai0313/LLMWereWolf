"""Main GameEngine class that combines all mixins."""

from llm_werewolf.core.engine.base import GameEngineBase
from llm_werewolf.core.engine.day_phase import DayPhaseMixin
from llm_werewolf.core.engine.night_phase import NightPhaseMixin
from llm_werewolf.core.engine.voting_phase import VotingPhaseMixin
from llm_werewolf.core.engine.death_handler import DeathHandlerMixin
from llm_werewolf.core.engine.action_processor import ActionProcessorMixin
from llm_werewolf.core.engine.sheriff_election import SheriffElectionMixin


class GameEngine(
    DeathHandlerMixin,
    ActionProcessorMixin,
    NightPhaseMixin,
    SheriffElectionMixin,
    DayPhaseMixin,
    VotingPhaseMixin,
    GameEngineBase,
):
    """Core game engine that controls the flow of the Werewolf game.

    This class combines multiple mixins to organize game logic:
    - GameEngineBase: Core initialization and game loop
    - DeathHandlerMixin: Death-related logic (werewolf kills, lover deaths, etc.)
    - ActionProcessorMixin: Processing game actions
    - NightPhaseMixin: Night phase execution
    - SheriffElectionMixin: Sheriff election phase execution
    - DayPhaseMixin: Day discussion phase execution
    - VotingPhaseMixin: Voting phase execution
    """

    pass
