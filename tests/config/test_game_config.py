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


def test_6_players_config() -> None:
    """Test config for 6 players (minimum)."""
    config = create_game_config_from_player_count(6)
    assert config.num_players == 6
    assert len(config.role_names) == 6
    # 6 players: 2 werewolves, Seer, Witch, 2 villagers
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 2
    assert "Seer" in config.role_names
    assert "Witch" in config.role_names
    assert "Guard" not in config.role_names  # Guard at 7+
    # Check timeouts
    assert config.night_timeout == 45
    assert config.day_timeout == 180
    assert config.vote_timeout == 45


def test_7_players_config() -> None:
    """Test config for 7 players (Guard threshold)."""
    config = create_game_config_from_player_count(7)
    assert config.num_players == 7
    assert len(config.role_names) == 7
    # Should have Guard now
    assert "Guard" in config.role_names
    assert "Hunter" not in config.role_names  # Hunter at 9+


def test_8_players_config() -> None:
    """Test config for 8 players."""
    config = create_game_config_from_player_count(8)
    assert config.num_players == 8
    assert len(config.role_names) == 8
    # Still 2 werewolves
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 2
    # Timeouts should still be small game settings
    assert config.night_timeout == 45
    assert config.day_timeout == 180


def test_9_players_config() -> None:
    """Test config for 9 players (AlphaWolf threshold)."""
    config = create_game_config_from_player_count(9)
    assert config.num_players == 9
    assert len(config.role_names) == 9
    # Should have 3 werewolves now (2 + AlphaWolf)
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 3
    assert "AlphaWolf" in config.role_names
    assert "Hunter" in config.role_names
    # Timeouts should transition to medium game settings
    assert config.night_timeout == 60
    assert config.day_timeout == 300


def test_11_players_config() -> None:
    """Test config for 11 players (Cupid threshold)."""
    config = create_game_config_from_player_count(11)
    assert config.num_players == 11
    assert len(config.role_names) == 11
    # Should have Cupid now
    assert "Cupid" in config.role_names
    # Still 3 werewolves
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 3


def test_12_players_config() -> None:
    """Test config for 12 players (WhiteWolf threshold)."""
    config = create_game_config_from_player_count(12)
    assert config.num_players == 12
    assert len(config.role_names) == 12
    # Should have 4 werewolves now (2 + AlphaWolf + WhiteWolf)
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 4
    assert "WhiteWolf" in config.role_names
    # Still medium game timeouts
    assert config.night_timeout == 60
    assert config.day_timeout == 300


def test_13_players_config() -> None:
    """Test config for 13 players (Idiot threshold)."""
    config = create_game_config_from_player_count(13)
    assert config.num_players == 13
    assert len(config.role_names) == 13
    # Should have Idiot now
    assert "Idiot" in config.role_names
    # Timeouts should transition to large game settings
    assert config.night_timeout == 90
    assert config.day_timeout == 400


def test_15_players_config() -> None:
    """Test config for 15 players (WolfBeauty and Elder threshold)."""
    config = create_game_config_from_player_count(15)
    assert config.num_players == 15
    assert len(config.role_names) == 15
    # Should have 5 werewolves now (2 + AlphaWolf + WhiteWolf + WolfBeauty)
    werewolves = sum(1 for role in config.role_names if "Wolf" in role or role == "Werewolf")
    assert werewolves == 5
    assert "WolfBeauty" in config.role_names
    assert "Elder" in config.role_names


def test_17_players_config() -> None:
    """Test config for 17 players (Knight threshold)."""
    config = create_game_config_from_player_count(17)
    assert config.num_players == 17
    assert len(config.role_names) == 17
    # Should have Knight now
    assert "Knight" in config.role_names


def test_19_players_config() -> None:
    """Test config for 19 players (Raven threshold)."""
    config = create_game_config_from_player_count(19)
    assert config.num_players == 19
    assert len(config.role_names) == 19
    # Should have Raven now
    assert "Raven" in config.role_names


def test_20_players_config() -> None:
    """Test config for 20 players (maximum)."""
    config = create_game_config_from_player_count(20)
    assert config.num_players == 20
    assert len(config.role_names) == 20
    # Should have all roles
    assert "Raven" in config.role_names
    # Large game timeouts
    assert config.night_timeout == 90
    assert config.day_timeout == 400
    assert config.vote_timeout == 90


def test_villager_count() -> None:
    """Test that villagers fill remaining slots correctly."""
    for num_players in range(6, 21):
        config = create_game_config_from_player_count(num_players)
        villager_count = sum(1 for role in config.role_names if role == "Villager")
        special_roles = sum(1 for role in config.role_names if role != "Villager")
        assert villager_count + special_roles == num_players
        assert villager_count >= 0
