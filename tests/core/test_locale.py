"""Tests for core/locale.py module."""

from llm_werewolf.core.locale import Locale


class TestLocale:
    """Tests for Locale class."""

    def test_default_language(self) -> None:
        """Test that default language is en-US."""
        locale = Locale()
        assert locale.language == "en-US"

    def test_english_locale(self) -> None:
        """Test English locale initialization."""
        locale = Locale("en-US")
        assert locale.language == "en-US"
        assert "night_begins" in locale.messages

    def test_traditional_chinese_locale(self) -> None:
        """Test Traditional Chinese locale initialization."""
        locale = Locale("zh-TW")
        assert locale.language == "zh-TW"
        assert "night_begins" in locale.messages

    def test_simplified_chinese_locale(self) -> None:
        """Test Simplified Chinese locale initialization."""
        locale = Locale("zh-CN")
        assert locale.language == "zh-CN"
        assert "night_begins" in locale.messages

    def test_unsupported_language_fallback(self) -> None:
        """Test that unsupported language falls back to English."""
        locale = Locale("fr-FR")
        assert locale.language == "en-US"
        # Should still have English messages
        assert locale.get("night_begins") == "Night {round_number} begins"

    def test_get_message_without_formatting(self) -> None:
        """Test getting a message without formatting."""
        locale = Locale("en-US")
        message = locale.get("voting_phase")
        assert message == "Voting Phase"

    def test_get_message_with_formatting(self) -> None:
        """Test getting a message with formatting."""
        locale = Locale("en-US")
        message = locale.get("night_begins", round_number=3)
        assert message == "Night 3 begins"

    def test_get_message_with_multiple_params(self) -> None:
        """Test getting a message with multiple parameters."""
        locale = Locale("en-US")
        message = locale.get("game_started", player_count=9)
        assert message == "Game started with 9 players"

    def test_get_nonexistent_key(self) -> None:
        """Test that nonexistent key returns the key itself."""
        locale = Locale("en-US")
        message = locale.get("nonexistent_key")
        assert message == "nonexistent_key"

    def test_get_message_with_wrong_format_params(self) -> None:
        """Test getting a message with wrong format parameters."""
        locale = Locale("en-US")
        # night_begins expects round_number, but we provide player_count
        message = locale.get("night_begins", player_count=5)
        # Should return template as-is when formatting fails
        assert message == "Night {round_number} begins"

    def test_set_language_to_chinese(self) -> None:
        """Test changing language to Chinese."""
        locale = Locale("en-US")
        assert locale.language == "en-US"

        locale.set_language("zh-TW")
        assert locale.language == "zh-TW"
        # Check that messages are now in Chinese
        message = locale.get("voting_phase")
        assert message == "投票階段"

    def test_set_language_to_english(self) -> None:
        """Test changing language to English."""
        locale = Locale("zh-TW")
        assert locale.language == "zh-TW"

        locale.set_language("en-US")
        assert locale.language == "en-US"
        # Check that messages are now in English
        message = locale.get("voting_phase")
        assert message == "Voting Phase"

    def test_set_language_invalid(self) -> None:
        """Test that setting invalid language has no effect."""
        locale = Locale("en-US")
        assert locale.language == "en-US"

        locale.set_language("invalid-LANG")
        # Should remain English
        assert locale.language == "en-US"
        message = locale.get("voting_phase")
        assert message == "Voting Phase"

    def test_all_locales_have_same_keys(self) -> None:
        """Test that all locales have the same message keys."""
        en_keys = set(Locale.MESSAGES["en-US"].keys())
        tw_keys = set(Locale.MESSAGES["zh-TW"].keys())
        cn_keys = set(Locale.MESSAGES["zh-CN"].keys())

        assert en_keys == tw_keys
        assert en_keys == cn_keys

    def test_phase_separator_messages(self) -> None:
        """Test phase separator messages."""
        locale = Locale("en-US")
        assert locale.get("phase_separator") == "=" * 60
        assert "🌙" in locale.get("night_separator")
        assert "☀️" in locale.get("day_separator")

    def test_vote_messages(self) -> None:
        """Test vote-related messages."""
        locale = Locale("en-US")
        vote_cast = locale.get("vote_cast", voter="Alice", target="Bob")
        assert "Alice" in vote_cast
        assert "Bob" in vote_cast

    def test_death_messages(self) -> None:
        """Test death-related messages."""
        locale = Locale("en-US")
        killed = locale.get("killed_by_werewolves", player="Alice")
        assert "Alice" in killed
        assert "werewolves" in killed.lower()

    def test_role_action_messages(self) -> None:
        """Test role action messages."""
        locale = Locale("en-US")

        witch_saved = locale.get("witch_saved", target="Bob")
        assert "Witch" in witch_saved
        assert "Bob" in witch_saved

        guard_protected = locale.get("guard_protected", target="Charlie")
        assert "Guard" in guard_protected
        assert "Charlie" in guard_protected

    def test_chinese_messages_formatting(self) -> None:
        """Test that Chinese messages support formatting."""
        locale = Locale("zh-TW")

        message = locale.get("night_begins", round_number=5)
        assert "5" in message
        assert "黑夜" in message

        message = locale.get("game_started", player_count=10)
        assert "10" in message
