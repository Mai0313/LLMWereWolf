"""Tests for Player class."""

from llm_werewolf.core.roles import Villager, Werewolf
from llm_werewolf.core.player import Player, PlayerStatus


def test_player_creation():
    """Test creating a player."""
    player = Player("p1", "Alice", Villager)

    assert player.player_id == "p1"
    assert player.name == "Alice"
    assert player.is_alive()
    assert player.can_vote()


def test_player_death():
    """Test player death."""
    player = Player("p1", "Alice", Villager)

    player.kill()
    assert not player.is_alive()
    assert player.has_status(PlayerStatus.DEAD)


def test_player_revive():
    """Test player revival."""
    player = Player("p1", "Alice", Villager)

    player.kill()
    assert not player.is_alive()

    player.revive()
    assert player.is_alive()
    assert player.has_status(PlayerStatus.ALIVE)


def test_player_status():
    """Test player status management."""
    player = Player("p1", "Alice", Villager)

    player.add_status(PlayerStatus.PROTECTED)
    assert player.has_status(PlayerStatus.PROTECTED)

    player.remove_status(PlayerStatus.PROTECTED)
    assert not player.has_status(PlayerStatus.PROTECTED)


def test_player_voting_rights():
    """Test player voting rights."""
    player = Player("p1", "Alice", Villager)

    assert player.can_vote()

    player.disable_voting()
    assert not player.can_vote()
    assert player.has_status(PlayerStatus.NO_VOTE)


def test_player_lover_status():
    """Test player lover status."""
    player = Player("p1", "Alice", Villager)

    assert not player.is_lover()

    player.set_lover("p2")
    assert player.is_lover()
    assert player.lover_partner_id == "p2"


def test_player_public_info():
    """Test getting public player info."""
    player = Player("p1", "Bob", Werewolf, ai_model="gpt-4")

    info = player.get_public_info()
    assert info.player_id == "p1"
    assert info.name == "Bob"
    assert info.is_alive
    assert info.ai_model == "gpt-4"
