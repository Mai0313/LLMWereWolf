"""Tests for role classes."""

from unittest.mock import patch

from llm_werewolf.core.roles import Camp, Seer, Guard, Witch, Villager, Werewolf
from llm_werewolf.core.player import Player
from llm_werewolf.core.actions import (
    SeerCheckAction,
    WitchSaveAction,
    WitchPoisonAction,
    GuardProtectAction,
    WerewolfKillAction,
)
from llm_werewolf.core.game_state import GameState


def test_villager_role():
    """Test villager role creation."""
    player = Player("p1", "Alice", Villager)
    villager = player.role
    assert villager.name == "Villager"
    assert villager.camp == Camp.VILLAGER
    assert not villager.config.can_act_night
    assert not villager.config.can_act_day


def test_werewolf_role():
    """Test werewolf role creation."""
    player = Player("p1", "Alice", Werewolf)
    werewolf = player.role
    assert werewolf.name == "Werewolf"
    assert werewolf.camp == Camp.WEREWOLF
    assert werewolf.config.can_act_night
    assert werewolf.config.priority is not None


def test_seer_role():
    """Test seer role creation."""
    player = Player("p1", "Alice", Seer)
    seer = player.role
    assert seer.name == "Seer"
    assert seer.camp == Camp.VILLAGER
    assert seer.config.can_act_night


def test_witch_role():
    """Test witch role with potions."""
    player = Player("p1", "Alice", Witch)
    witch: Witch = player.role
    assert witch.name == "Witch"
    assert witch.camp == Camp.VILLAGER
    assert witch.has_save_potion
    assert witch.has_poison_potion


def test_role_string_representation():
    """Test role string representation."""
    player = Player("p1", "Alice", Villager)
    villager = player.role
    assert str(villager) == "Villager"
    assert "Villager" in repr(villager)


def test_werewolf_get_night_actions():
    """Test Werewolf get_night_actions method."""
    werewolf_player = Player("p1", "Werewolf", Werewolf)
    villager_player = Player("p2", "Villager", Villager)
    players = [werewolf_player, villager_player]
    game_state = GameState(players)

    with patch("random.choice", return_value=villager_player):
        actions = werewolf_player.role.get_night_actions(game_state)
        assert len(actions) == 1
        assert isinstance(actions[0], WerewolfKillAction)
        assert actions[0].target == villager_player


def test_seer_get_night_actions():
    """Test Seer get_night_actions method."""
    seer_player = Player("p1", "Seer", Seer)
    villager_player = Player("p2", "Villager", Villager)
    players = [seer_player, villager_player]
    game_state = GameState(players)

    with patch("random.choice", return_value=villager_player):
        actions = seer_player.role.get_night_actions(game_state)
        assert len(actions) == 1
        assert isinstance(actions[0], SeerCheckAction)
        assert actions[0].target == villager_player


def test_witch_get_night_actions_save():
    """Test Witch get_night_actions method for saving."""
    witch_player = Player("p1", "Witch", Witch)
    villager_player = Player("p2", "Villager", Villager)
    players = [witch_player, villager_player]
    game_state = GameState(players)
    game_state.werewolf_target = "p2"

    with patch("random.choice", return_value=True):
        actions = witch_player.role.get_night_actions(game_state)
        assert len(actions) == 1
        assert isinstance(actions[0], WitchSaveAction)
        assert actions[0].target == villager_player


def test_witch_get_night_actions_poison():
    """Test Witch get_night_actions method for poisoning."""
    witch_player = Player("p1", "Witch", Witch)
    villager_player = Player("p2", "Villager", Villager)
    players = [witch_player, villager_player]
    game_state = GameState(players)
    witch_player.role.has_save_potion = False

    with patch("random.choice", return_value=villager_player):
        actions = witch_player.role.get_night_actions(game_state)
        if actions:
            assert len(actions) == 1
            assert isinstance(actions[0], WitchPoisonAction)
            assert actions[0].target == villager_player


def test_guard_get_night_actions():
    """Test Guard get_night_actions method."""
    guard_player = Player("p1", "Guard", Guard)
    villager_player = Player("p2", "Villager", Villager)
    players = [guard_player, villager_player]
    game_state = GameState(players)

    with patch("random.choice", return_value=villager_player):
        actions = guard_player.role.get_night_actions(game_state)
        assert len(actions) == 1
        assert isinstance(actions[0], GuardProtectAction)
        assert actions[0].target == villager_player
