"""Tests for core/victory.py module."""

from llm_werewolf.core.roles import Seer, Witch, Villager, Werewolf
from llm_werewolf.core.player import Player
from llm_werewolf.core.victory import VictoryChecker
from llm_werewolf.core.game_state import GameState


class TestVictoryChecker:
    """Tests for VictoryChecker class."""

    def create_mock_player(
        self, player_id: str, name: str, role_class: type, is_alive: bool = True
    ) -> Player:
        """Create a mock player for testing."""
        player = Player(player_id=player_id, name=name, role=role_class)
        if not is_alive:
            player.kill()
        return player

    def test_werewolf_victory_equal_numbers(self) -> None:
        """Test werewolves win when equal to villagers."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("w2", "Wolf2", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_werewolf_victory()

        assert result.has_winner is True
        assert result.winner_camp == "werewolf"
        assert len(result.winner_ids) == 2
        assert "w1" in result.winner_ids
        assert "w2" in result.winner_ids
        assert "equal or outnumber villagers" in result.reason

    def test_werewolf_victory_outnumber(self) -> None:
        """Test werewolves win when outnumber villagers."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("w2", "Wolf2", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_werewolf_victory()

        assert result.has_winner is True
        assert result.winner_camp == "werewolf"
        assert len(result.winner_ids) == 2

    def test_werewolf_not_won_yet(self) -> None:
        """Test werewolves have not won yet."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
            self.create_mock_player("v3", "Villager3", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_werewolf_victory()

        assert result.has_winner is False
        assert "have not won" in result.reason

    def test_werewolf_all_dead(self) -> None:
        """Test werewolves cannot win if all dead."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("w2", "Wolf2", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_werewolf_victory()

        assert result.has_winner is False

    def test_villager_victory_all_werewolves_dead(self) -> None:
        """Test villagers win when all werewolves are dead."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("w2", "Wolf2", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Seer),
            self.create_mock_player("v3", "Villager3", Witch),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_villager_victory()

        assert result.has_winner is True
        assert result.winner_camp == "villager"
        assert len(result.winner_ids) == 3
        assert "v1" in result.winner_ids
        assert "v2" in result.winner_ids
        assert "v3" in result.winner_ids
        assert "eliminated" in result.reason

    def test_villager_not_won_yet(self) -> None:
        """Test villagers have not won yet."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_villager_victory()

        assert result.has_winner is False
        assert "have not won" in result.reason

    def test_lover_victory(self) -> None:
        """Test lovers win when only they remain."""
        players = [
            self.create_mock_player("p1", "Player1", Villager),
            self.create_mock_player("p2", "Player2", Werewolf),
            self.create_mock_player("p3", "Player3", Villager, is_alive=False),
            self.create_mock_player("p4", "Player4", Werewolf, is_alive=False),
        ]
        # Set lovers
        players[0].set_lover("p2")
        players[1].set_lover("p1")

        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_lover_victory()

        assert result.has_winner is True
        assert result.winner_camp == "lover"
        assert len(result.winner_ids) == 2
        assert "p1" in result.winner_ids
        assert "p2" in result.winner_ids
        assert "only the lovers remain" in result.reason.lower()

    def test_lover_not_won_more_alive(self) -> None:
        """Test lovers have not won when more than 2 alive."""
        players = [
            self.create_mock_player("p1", "Player1", Villager),
            self.create_mock_player("p2", "Player2", Werewolf),
            self.create_mock_player("p3", "Player3", Villager),
        ]
        # Set lovers
        players[0].set_lover("p2")
        players[1].set_lover("p1")

        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_lover_victory()

        assert result.has_winner is False

    def test_lover_not_won_one_dead(self) -> None:
        """Test lovers have not won when one lover is dead."""
        players = [
            self.create_mock_player("p1", "Player1", Villager),
            self.create_mock_player("p2", "Player2", Werewolf, is_alive=False),
            self.create_mock_player("p3", "Player3", Villager),
        ]
        # Set lovers
        players[0].set_lover("p2")
        players[1].set_lover("p1")

        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_lover_victory()

        assert result.has_winner is False

    def test_check_victory_priority_lover_first(self) -> None:
        """Test that lover victory is checked first."""
        players = [
            self.create_mock_player("p1", "Player1", Villager),
            self.create_mock_player("p2", "Player2", Werewolf),
            self.create_mock_player("p3", "Player3", Villager, is_alive=False),
        ]
        # Set lovers
        players[0].set_lover("p2")
        players[1].set_lover("p1")

        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_victory()

        # Lovers should win even though werewolves could also win
        assert result.has_winner is True
        assert result.winner_camp == "lover"

    def test_check_victory_werewolf_wins(self) -> None:
        """Test check_victory returns werewolf victory."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("w2", "Wolf2", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_victory()

        assert result.has_winner is True
        assert result.winner_camp == "werewolf"

    def test_check_victory_villager_wins(self) -> None:
        """Test check_victory returns villager victory."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_victory()

        assert result.has_winner is True
        assert result.winner_camp == "villager"

    def test_check_victory_no_winner(self) -> None:
        """Test check_victory returns no winner when game continues."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
            self.create_mock_player("v3", "Villager3", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_victory()

        assert result.has_winner is False
        assert "continues" in result.reason

    def test_check_special_victory(self) -> None:
        """Test check_special_victory always returns no winner."""
        players = [self.create_mock_player("p1", "Player1", Villager)]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.check_special_victory()

        assert result.has_winner is False
        assert "special" in result.reason.lower()

    def test_get_winner(self) -> None:
        """Test get_winner delegates to check_victory."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        result = checker.get_winner()

        assert result.has_winner is True
        assert result.winner_camp == "villager"

    def test_is_game_over_true(self) -> None:
        """Test is_game_over returns True when there's a winner."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        assert checker.is_game_over() is True

    def test_is_game_over_false(self) -> None:
        """Test is_game_over returns False when game continues."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        assert checker.is_game_over() is False

    def test_get_winning_players(self) -> None:
        """Test get_winning_players returns correct players."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Seer),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        winning_players = checker.get_winning_players()

        assert len(winning_players) == 2
        assert winning_players[0].player_id in ["v1", "v2"]
        assert winning_players[1].player_id in ["v1", "v2"]

    def test_get_winning_players_no_winner(self) -> None:
        """Test get_winning_players returns empty list when no winner."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        winning_players = checker.get_winning_players()

        assert len(winning_players) == 0

    def test_get_losing_players(self) -> None:
        """Test get_losing_players returns correct players."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf, is_alive=False),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Seer),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        losing_players = checker.get_losing_players()

        assert len(losing_players) == 1
        assert losing_players[0].player_id == "w1"

    def test_get_losing_players_no_winner(self) -> None:
        """Test get_losing_players returns empty list when no winner."""
        players = [
            self.create_mock_player("w1", "Wolf1", Werewolf),
            self.create_mock_player("v1", "Villager1", Villager),
            self.create_mock_player("v2", "Villager2", Villager),
        ]
        game_state = GameState(players=players)
        checker = VictoryChecker(game_state)

        losing_players = checker.get_losing_players()

        assert len(losing_players) == 0
