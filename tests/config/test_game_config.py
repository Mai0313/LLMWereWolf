import pytest
from pydantic import ValidationError

from llm_werewolf.core.config import GameConfig, create_game_config_from_player_count
from llm_werewolf.core.role_registry import create_roles


def test_valid_game_config() -> None:
    """Test creating a valid game configuration."""
    config = GameConfig(
        num_players=9,
        role_names=[
            "Werewolf",
            "Werewolf",
            "Seer",
            "Witch",
            "Hunter",
            "Guard",
            "Villager",
            "Villager",
            "Villager",
        ],
    )

    assert config.num_players == 9
    assert len(config.role_names) == 9


def test_invalid_player_count() -> None:
    """Test invalid player count."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=3,  # Too few
            role_names=["Werewolf", "Villager", "Villager"],
        )


def test_role_count_mismatch() -> None:
    """Test role count not matching player count."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=9,
            role_names=["Werewolf", "Villager"],  # Only 2 roles
        )


def test_no_werewolf() -> None:
    """Test configuration with no werewolves."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=6,
            role_names=["Villager"] * 6,  # No werewolves
        )


def test_config_to_role_list() -> None:
    """Test converting config to role instances."""
    config = create_game_config_from_player_count(6)
    roles = create_roles(config.role_names)

    assert len(roles) == 6
    assert all(hasattr(role, "name") for role in roles)


def test_create_game_config_from_player_count() -> None:
    """Test auto-generating game config by player count."""
    config = create_game_config_from_player_count(9)
    assert config.num_players == 9
    assert len(config.role_names) == 9
    # 9 players should have 2-3 werewolves
    werewolf_count = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert 2 <= werewolf_count <= 3


def test_invalid_player_count_config() -> None:
    """Test auto-config with invalid player count."""
    with pytest.raises(ValueError, match="Maximum 20 players supported"):
        create_game_config_from_player_count(100)

    with pytest.raises(ValueError, match="Minimum 6 players required"):
        create_game_config_from_player_count(3)


def test_config_scaling() -> None:
    """Test that role composition scales with player count."""
    config_6 = create_game_config_from_player_count(6)
    config_12 = create_game_config_from_player_count(12)

    # More players should mean more werewolves
    werewolves_6 = sum(1 for role in config_6.role_names if "Wolf" in role or role == "Werewolf")
    werewolves_12 = sum(1 for role in config_12.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves_12 >= werewolves_6
