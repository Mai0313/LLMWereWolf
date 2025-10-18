"""Integration tests for game flow."""

from llm_werewolf.ai import DemoAgent
from llm_werewolf.core import GameEngine
from llm_werewolf.config import PRESET_6_PLAYERS


def test_game_initialization():
    """Test initializing a game."""
    config = PRESET_6_PLAYERS
    engine = GameEngine(config)

    # Create players
    players = []
    for i in range(config.num_players):
        players.append((f"p{i}", f"Player{i}", DemoAgent()))

    # Get roles
    roles = config.to_role_list()

    # Setup game
    engine.setup_game(players, roles)

    assert engine.game_state is not None
    assert len(engine.game_state.players) == 6


def test_game_state_initialization():
    """Test game state after initialization."""
    config = PRESET_6_PLAYERS
    engine = GameEngine(config)

    players = [(f"p{i}", f"Player{i}", DemoAgent()) for i in range(config.num_players)]
    roles = config.to_role_list()

    engine.setup_game(players, roles)

    assert engine.game_state.phase.value == "setup"
    assert engine.game_state.round_number == 0
    assert len(engine.game_state.get_alive_players()) == 6


def test_role_assignment():
    """Test that roles are properly assigned."""
    config = PRESET_6_PLAYERS
    engine = GameEngine(config)

    players = [(f"p{i}", f"Player{i}", DemoAgent()) for i in range(config.num_players)]
    roles = config.to_role_list()

    engine.setup_game(players, roles)

    role_assignments = engine.assign_roles()
    assert len(role_assignments) == 6

    # Check that each player has a role
    for player_id, role_name in role_assignments.items():
        player = engine.game_state.get_player(player_id)
        assert player is not None
        assert player.get_role_name() == role_name


def test_victory_checker():
    """Test victory condition checking."""
    config = PRESET_6_PLAYERS
    engine = GameEngine(config)

    players = [(f"p{i}", f"Player{i}", DemoAgent()) for i in range(config.num_players)]
    roles = config.to_role_list()

    engine.setup_game(players, roles)

    # Initially no winner
    assert not engine.check_victory()

    # Kill all werewolves (villagers should win)
    for player in engine.game_state.players:
        if player.get_camp() == "werewolf":
            player.kill()

    # Now villagers should win
    assert engine.check_victory()
    assert engine.game_state.winner == "villager"
