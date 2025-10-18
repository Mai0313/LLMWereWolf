"""Tests for game configuration."""

import pytest
from pydantic import ValidationError

from llm_werewolf.config import (
    PRESET_6_PLAYERS,
    GameConfig,
    get_preset,
    list_preset_names,
    get_preset_by_name,
)


def test_valid_game_config():
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


def test_invalid_player_count():
    """Test invalid player count."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=3,  # Too few
            role_names=["Werewolf", "Villager", "Villager"],
        )


def test_role_count_mismatch():
    """Test role count not matching player count."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=9,
            role_names=["Werewolf", "Villager"],  # Only 2 roles
        )


def test_no_werewolf():
    """Test configuration with no werewolves."""
    with pytest.raises(ValidationError):
        GameConfig(
            num_players=6,
            role_names=["Villager"] * 6,  # No werewolves
        )


def test_config_to_role_list():
    """Test converting config to role instances."""
    config = PRESET_6_PLAYERS
    roles = config.to_role_list()

    assert len(roles) == 6
    assert all(hasattr(role, "name") for role in roles)


def test_get_preset():
    """Test getting preset by player count."""
    preset = get_preset(9)
    assert preset.num_players == 9


def test_invalid_preset():
    """Test getting preset with invalid player count."""
    with pytest.raises(ValueError, match="Maximum 20 players supported"):
        get_preset(100)


def test_get_preset_by_name():
    """Test getting preset by name."""
    preset = get_preset_by_name("9-players")
    assert preset.num_players == 9


def test_list_preset_names():
    """Test listing all preset names."""
    names = list_preset_names()
    assert "9-players" in names
    assert "6-players" in names
    assert isinstance(names, list)
