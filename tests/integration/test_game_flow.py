from llm_werewolf.core import GameEngine
from llm_werewolf.core.agent import DemoAgent
from llm_werewolf.core.config import create_game_config_from_player_count
from llm_werewolf.core.role_registry import create_roles


def test_game_initialization() -> None:
    """Test initializing a game."""
    config = create_game_config_from_player_count(6)
    engine = GameEngine(config)

    # Create players
    players = []
    for i in range(config.num_players):
        players.append(DemoAgent(name=f"Player{i}", model="demo"))

    # Get roles
    roles = create_roles(role_names=config.role_names)

    # Setup game
    engine.setup_game(players=players, roles=roles)

    assert engine.game_state is not None
    assert len(engine.game_state.players) == 6


def test_game_state_initialization() -> None:
    """Test game state after initialization."""
    config = create_game_config_from_player_count(6)
    engine = GameEngine(config)

    players = [DemoAgent(name=f"Player{i}", model="demo") for i in range(config.num_players)]
    roles = create_roles(role_names=config.role_names)

    engine.setup_game(players=players, roles=roles)

    assert engine.game_state.phase.value == "setup"
    assert engine.game_state.round_number == 0
    assert len(engine.game_state.get_alive_players()) == 6


def test_role_assignment() -> None:
    """Test that roles are properly assigned."""
    config = create_game_config_from_player_count(6)
    engine = GameEngine(config)

    players = [DemoAgent(name=f"Player{i}", model="demo") for i in range(config.num_players)]
    roles = create_roles(role_names=config.role_names)

    engine.setup_game(players=players, roles=roles)

    role_assignments = engine.assign_roles()
    assert len(role_assignments) == 6

    # Check that each player has a role
    for player_id, role_name in role_assignments.items():
        player = engine.game_state.get_player(player_id)
        assert player is not None
        assert player.get_role_name() == role_name


def test_victory_checker() -> None:
    """Test victory condition checking."""
    config = create_game_config_from_player_count(6)
    engine = GameEngine(config)

    players = [DemoAgent(name=f"Player{i}", model="demo") for i in range(config.num_players)]
    roles = create_roles(role_names=config.role_names)

    engine.setup_game(players=players, roles=roles)

    # Initially no winner
    assert not engine.check_victory()

    # Kill all werewolves (villagers should win)
    for player in engine.game_state.players:
        if player.get_camp() == "werewolf":
            player.kill()

    # Now villagers should win
    assert engine.check_victory()
    assert engine.game_state.winner == "villager"
