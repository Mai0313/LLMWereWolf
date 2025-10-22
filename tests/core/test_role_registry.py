"""Tests for core/role_registry.py module."""

import pytest

from llm_werewolf.core.roles import Seer, Witch, Villager, Werewolf, AlphaWolf, WhiteWolf
from llm_werewolf.core.roles.base import Role
from llm_werewolf.core.role_registry import (
    create_roles,
    get_role_map,
    get_werewolf_roles,
    validate_role_names,
)


class TestGetRoleMap:
    """Tests for get_role_map function."""

    def test_get_role_map_returns_dict(self) -> None:
        """Test that get_role_map returns a dictionary."""
        role_map = get_role_map()
        assert isinstance(role_map, dict)

    def test_get_role_map_contains_werewolf(self) -> None:
        """Test that role map contains Werewolf."""
        role_map = get_role_map()
        assert "Werewolf" in role_map
        assert role_map["Werewolf"] == Werewolf

    def test_get_role_map_contains_villager_roles(self) -> None:
        """Test that role map contains villager roles."""
        role_map = get_role_map()
        assert "Villager" in role_map
        assert "Seer" in role_map
        assert "Witch" in role_map
        assert "Hunter" in role_map
        assert "Guard" in role_map

    def test_get_role_map_contains_special_werewolves(self) -> None:
        """Test that role map contains special werewolf roles."""
        role_map = get_role_map()
        assert "AlphaWolf" in role_map
        assert "WhiteWolf" in role_map
        assert "WolfBeauty" in role_map
        assert "HiddenWolf" in role_map

    def test_get_role_map_all_values_are_role_classes(self) -> None:
        """Test that all values in role map are Role classes."""
        role_map = get_role_map()
        for role_class in role_map.values():
            assert issubclass(role_class, Role)


class TestGetWerewolfRoles:
    """Tests for get_werewolf_roles function."""

    def test_get_werewolf_roles_returns_set(self) -> None:
        """Test that get_werewolf_roles returns a set."""
        werewolf_roles = get_werewolf_roles()
        assert isinstance(werewolf_roles, set)

    def test_get_werewolf_roles_contains_werewolf(self) -> None:
        """Test that werewolf roles contains Werewolf."""
        werewolf_roles = get_werewolf_roles()
        assert "Werewolf" in werewolf_roles

    def test_get_werewolf_roles_contains_special_werewolves(self) -> None:
        """Test that werewolf roles contains special werewolves."""
        werewolf_roles = get_werewolf_roles()
        assert "AlphaWolf" in werewolf_roles
        assert "WhiteWolf" in werewolf_roles
        assert "WolfBeauty" in werewolf_roles
        assert "HiddenWolf" in werewolf_roles

    def test_get_werewolf_roles_not_contains_villager(self) -> None:
        """Test that werewolf roles doesn't contain villager roles."""
        werewolf_roles = get_werewolf_roles()
        assert "Villager" not in werewolf_roles
        assert "Seer" not in werewolf_roles
        assert "Witch" not in werewolf_roles


class TestValidateRoleNames:
    """Tests for validate_role_names function."""

    def test_validate_valid_role_names(self) -> None:
        """Test validating valid role names."""
        role_names = ["Werewolf", "Werewolf", "Villager", "Seer", "Witch"]
        # Should not raise any exception
        validate_role_names(role_names)

    def test_validate_with_special_werewolves(self) -> None:
        """Test validating with special werewolf roles."""
        role_names = ["AlphaWolf", "WhiteWolf", "Villager", "Seer"]
        # Should not raise any exception
        validate_role_names(role_names)

    def test_validate_unknown_role_raises_error(self) -> None:
        """Test that unknown role raises ValueError."""
        role_names = ["Werewolf", "UnknownRole", "Villager"]
        with pytest.raises(ValueError, match="Unknown role: UnknownRole"):
            validate_role_names(role_names)

    def test_validate_no_werewolf_raises_error(self) -> None:
        """Test that no werewolves raises ValueError."""
        role_names = ["Villager", "Seer", "Witch", "Hunter"]
        with pytest.raises(ValueError, match="At least one werewolf role is required"):
            validate_role_names(role_names)

    def test_validate_empty_list_raises_error(self) -> None:
        """Test that empty list raises ValueError."""
        role_names: list[str] = []
        with pytest.raises(ValueError, match="At least one werewolf role is required"):
            validate_role_names(role_names)

    def test_validate_single_werewolf(self) -> None:
        """Test that a single werewolf is valid."""
        role_names = ["Werewolf"]
        # Should not raise any exception
        validate_role_names(role_names)


class TestCreateRoles:
    """Tests for create_roles function."""

    def test_create_roles_returns_list(self) -> None:
        """Test that create_roles returns a list."""
        role_names = ["Werewolf", "Villager"]
        roles = create_roles(role_names)
        assert isinstance(roles, list)
        assert len(roles) == 2

    def test_create_roles_basic_roles(self) -> None:
        """Test creating basic roles."""
        role_names = ["Werewolf", "Villager", "Seer"]
        roles = create_roles(role_names)

        assert len(roles) == 3
        assert roles[0] == Werewolf
        assert roles[1] == Villager
        assert roles[2] == Seer

    def test_create_roles_special_werewolves(self) -> None:
        """Test creating special werewolf roles."""
        role_names = ["AlphaWolf", "WhiteWolf"]
        roles = create_roles(role_names)

        assert len(roles) == 2
        assert roles[0] == AlphaWolf
        assert roles[1] == WhiteWolf

    def test_create_roles_unknown_role_raises_error(self) -> None:
        """Test that unknown role raises ValueError."""
        role_names = ["Werewolf", "InvalidRole"]
        with pytest.raises(ValueError, match="Unknown role: InvalidRole"):
            create_roles(role_names)

    def test_create_roles_preserves_order(self) -> None:
        """Test that create_roles preserves order."""
        role_names = ["Seer", "Werewolf", "Witch", "Villager"]
        roles = create_roles(role_names)

        assert len(roles) == 4
        assert roles[0] == Seer
        assert roles[1] == Werewolf
        assert roles[2] == Witch
        assert roles[3] == Villager

    def test_create_roles_allows_duplicates(self) -> None:
        """Test that create_roles allows duplicate role names."""
        role_names = ["Werewolf", "Werewolf", "Villager", "Villager", "Villager"]
        roles = create_roles(role_names)

        assert len(roles) == 5
        assert roles[0] == Werewolf
        assert roles[1] == Werewolf
        assert roles[2] == Villager
        assert roles[3] == Villager
        assert roles[4] == Villager

    def test_create_roles_empty_list(self) -> None:
        """Test creating roles from empty list."""
        role_names: list[str] = []
        roles = create_roles(role_names)
        assert len(roles) == 0

    def test_create_roles_returns_role_classes(self) -> None:
        """Test that create_roles returns Role classes."""
        role_names = ["Werewolf", "Villager"]
        roles = create_roles(role_names)

        for role_class in roles:
            assert issubclass(role_class, Role)
