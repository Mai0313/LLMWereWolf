"""Tests for role classes."""

from llm_werewolf.core.roles import Camp, Seer, Witch, Villager, Werewolf


def test_villager_role():
    """Test villager role creation."""
    villager = Villager()
    assert villager.name == "Villager"
    assert villager.camp == Camp.VILLAGER
    assert not villager.config.can_act_night
    assert not villager.config.can_act_day


def test_werewolf_role():
    """Test werewolf role creation."""
    werewolf = Werewolf()
    assert werewolf.name == "Werewolf"
    assert werewolf.camp == Camp.WEREWOLF
    assert werewolf.config.can_act_night
    assert werewolf.config.priority is not None


def test_seer_role():
    """Test seer role creation."""
    seer = Seer()
    assert seer.name == "Seer"
    assert seer.camp == Camp.VILLAGER
    assert seer.config.can_act_night


def test_witch_role():
    """Test witch role with potions."""
    witch = Witch()
    assert witch.name == "Witch"
    assert witch.camp == Camp.VILLAGER
    assert witch.has_save_potion
    assert witch.has_poison_potion


def test_role_string_representation():
    """Test role string representation."""
    villager = Villager()
    assert str(villager) == "Villager"
    assert "Villager" in repr(villager)
