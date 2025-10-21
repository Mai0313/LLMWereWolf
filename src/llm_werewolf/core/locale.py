"""Localization support for game messages."""

from typing import ClassVar


class Locale:
    """Manages localized game messages."""

    # Message templates for different locales
    MESSAGES: ClassVar[dict[str, dict[str, str]]] = {
        "en-US": {
            # Phase transitions
            "night_begins": "Night {round_number} begins",
            "day_begins": "Day {round_number} begins",
            "voting_phase": "Voting Phase",
            "game_started": "Game started with {player_count} players",
            "game_ended": "Game ended. {winner} wins! {reason}",
            "game_over": "\nGame Over! {winner} camp wins!",
            # Phase separators
            "phase_separator": "=" * 60,
            "night_separator": "🌙 " + "=" * 56 + " 🌙",
            "day_separator": "☀️  " + "=" * 56 + " ☀️",
            # Player status
            "alive_players": "\nAlive Players:",
            "dead_players": "\nDead Players:",
            "player_role_info": "- {name} ({role})",
            # Deaths
            "player_died": "{player} died",
            "killed_by_werewolves": "{player} was killed by werewolves",
            "voted_out": "{player} was voted out",
            "player_eliminated": "{player} was eliminated by vote. They were a {role}.",
            "died_of_heartbreak": "{player} died of heartbreak (lover)!",
            "died_from_charm": "{player} died from Wolf Beauty's charm (Wolf Beauty {wolf_beauty} was eliminated)!",
            # Voting
            "vote_cast": "🗳️ {voter} votes for {target}",
            "vote_summary": "\n📊 Vote Summary:",
            "vote_count": "  {target}: {count} vote(s) - {voters}",
            "vote_tied": "Vote tied. No one is eliminated.",
            "no_votes": "No votes cast.",
            # Role actions
            "role_acting": "🎬 {role} ({player}) is acting...",
            "werewolf_voting": "🐺 Werewolves are discussing their target...",
            "werewolf_target": "🐺 Werewolves targeted {target}",
            "witch_saved": "💊 Witch saved {target}",
            "witch_poisoned": "☠️ Witch poisoned {target}",
            "guard_protected": "🛡️ Guard protected {target}",
            "seer_checked": "🔮 Seer checked {target}: {result}",
            "hunter_shoots": "🏹 Hunter {hunter} shoots {target}",
            "alpha_wolf_shoots": "🐺👑 Alpha Wolf {alpha} shoots {target}",
            "lovers_linked": "💕 Lovers linked: {player1} and {player2}",
            "white_wolf_kills": "🐺⚪ White Wolf kills {target}",
            "wolf_beauty_charms": "🐺💋 Wolf Beauty charms {target}",
            "cupid_links": "💘 Cupid links {player1} and {player2} as lovers",
            # Special cases
            "idiot_revealed": "{player} reveals they are the Idiot and survives!",
            "elder_executed": "The Elder was executed by the village! All villagers lose their special abilities as punishment!",
            "elder_attacked": "{player} was attacked but survived (Elder)!",
            "protected_by_guard": "{player} was protected by the guard!",
            "saved_by_witch": "{player} was saved by the witch!",
            "poisoned_no_ability": "{player} was poisoned by the Witch and cannot use their death ability.",
            "death_ability_active": "{player} ({role}) can shoot before dying!",
            # Config
            "config_loaded": "Loaded configuration: {config_path}",
            "preset_info": "Preset: {preset}",
            "interface_mode": "Interface mode: Console (auto-execute)",
        },
        "zh-TW": {
            # Phase transitions
            "night_begins": "第 {round_number} 輪黑夜開始",
            "day_begins": "第 {round_number} 輪白天開始",
            "voting_phase": "投票階段",
            "game_started": "遊戲開始，共有 {player_count} 位玩家",
            "game_ended": "遊戲結束。{winner} 獲勝!{reason}",
            "game_over": "\n遊戲結束!{winner} 陣營獲勝!",
            # Phase separators
            "phase_separator": "=" * 60,
            "night_separator": "🌙 " + "=" * 56 + " 🌙",
            "day_separator": "☀️  " + "=" * 56 + " ☀️",
            # Player status
            "alive_players": "\n存活玩家：",
            "dead_players": "\n淘汰玩家：",
            "player_role_info": "- {name}（{role}）",
            # Deaths
            "player_died": "{player} 死亡",
            "killed_by_werewolves": "{player} 被狼人殺害",
            "voted_out": "{player} 被投票淘汰",
            "player_eliminated": "{player} 被投票淘汰，身分是 {role}。",
            "died_of_heartbreak": "{player} 因愛而死（戀人）!",
            "died_from_charm": "{player} 被狼美人魅惑而死（狼美人 {wolf_beauty} 被淘汰）!",
            # Voting
            "vote_cast": "🗳️ {voter} 投票給 {target}",
            "vote_summary": "\n📊 投票統計：",
            "vote_count": "  {target}：{count} 票 - {voters}",
            "vote_tied": "投票平手，無人被淘汰。",
            "no_votes": "無人投票。",
            # Role actions
            "role_acting": "🎬 {role}（{player}）正在行動...",
            "werewolf_voting": "🐺 狼人正在討論目標...",
            "werewolf_target": "🐺 狼人選擇了 {target}",
            "witch_saved": "💊 女巫救了 {target}",
            "witch_poisoned": "☠️ 女巫毒殺了 {target}",
            "guard_protected": "🛡️ 守衛保護了 {target}",
            "seer_checked": "🔮 預言家查驗了 {target}：{result}",
            "hunter_shoots": "🏹 獵人 {hunter} 射殺了 {target}",
            "alpha_wolf_shoots": "🐺👑 狼王 {alpha} 帶走了 {target}",
            "lovers_linked": "💕 戀人連結：{player1} 和 {player2}",
            "white_wolf_kills": "🐺⚪ 白狼王殺了 {target}",
            "wolf_beauty_charms": "🐺💋 狼美人魅惑了 {target}",
            "cupid_links": "💘 丘比特將 {player1} 和 {player2} 連結為戀人",
            # Special cases
            "idiot_revealed": "{player} 揭示自己是白癡，倖免於難!",
            "elder_executed": "長老被村民處決了!所有村民失去特殊能力作為懲罰!",
            "elder_attacked": "{player} 被攻擊但倖存（長老）!",
            "protected_by_guard": "{player} 被守衛保護了!",
            "saved_by_witch": "{player} 被女巫救了!",
            "poisoned_no_ability": "{player} 被女巫毒殺，無法使用死亡技能。",
            "death_ability_active": "{player}（{role}）可以在死前射殺一人!",
            # Config
            "config_loaded": "已載入設定檔：{config_path}",
            "preset_info": "預設組合：{preset}",
            "interface_mode": "介面模式：Console（自動執行）",
        },
        "zh-CN": {
            # Phase transitions
            "night_begins": "第 {round_number} 轮黑夜开始",
            "day_begins": "第 {round_number} 轮白天开始",
            "voting_phase": "投票阶段",
            "game_started": "游戏开始，共有 {player_count} 位玩家",
            "game_ended": "游戏结束。{winner} 获胜!{reason}",
            "game_over": "\n游戏结束!{winner} 阵营获胜!",
            # Phase separators
            "phase_separator": "=" * 60,
            "night_separator": "🌙 " + "=" * 56 + " 🌙",
            "day_separator": "☀️  " + "=" * 56 + " ☀️",
            # Player status
            "alive_players": "\n存活玩家：",
            "dead_players": "\n淘汰玩家：",
            "player_role_info": "- {name}（{role}）",
            # Deaths
            "player_died": "{player} 死亡",
            "killed_by_werewolves": "{player} 被狼人杀害",
            "voted_out": "{player} 被投票淘汰",
            "player_eliminated": "{player} 被投票淘汰，身份是 {role}。",
            "died_of_heartbreak": "{player} 因爱而死（恋人）!",
            "died_from_charm": "{player} 被狼美人魅惑而死（狼美人 {wolf_beauty} 被淘汰）!",
            # Voting
            "vote_cast": "🗳️ {voter} 投票给 {target}",
            "vote_summary": "\n📊 投票统计：",
            "vote_count": "  {target}：{count} 票 - {voters}",
            "vote_tied": "投票平手，无人被淘汰。",
            "no_votes": "无人投票。",
            # Role actions
            "role_acting": "🎬 {role}（{player}）正在行动...",
            "werewolf_voting": "🐺 狼人正在讨论目标...",
            "werewolf_target": "🐺 狼人选择了 {target}",
            "witch_saved": "💊 女巫救了 {target}",
            "witch_poisoned": "☠️ 女巫毒杀了 {target}",
            "guard_protected": "🛡️ 守卫保护了 {target}",
            "seer_checked": "🔮 预言家查验了 {target}：{result}",
            "hunter_shoots": "🏹 猎人 {hunter} 射杀了 {target}",
            "alpha_wolf_shoots": "🐺👑 狼王 {alpha} 带走了 {target}",
            "lovers_linked": "💕 恋人连结：{player1} 和 {player2}",
            "white_wolf_kills": "🐺⚪ 白狼王杀了 {target}",
            "wolf_beauty_charms": "🐺💋 狼美人魅惑了 {target}",
            "cupid_links": "💘 丘比特将 {player1} 和 {player2} 连结为恋人",
            # Special cases
            "idiot_revealed": "{player} 揭示自己是白痴，幸免于难!",
            "elder_executed": "长老被村民处决了!所有村民失去特殊能力作为惩罚!",
            "elder_attacked": "{player} 被攻击但幸存（长老）!",
            "protected_by_guard": "{player} 被守卫保护了!",
            "saved_by_witch": "{player} 被女巫救了!",
            "poisoned_no_ability": "{player} 被女巫毒杀，无法使用死亡技能。",
            "death_ability_active": "{player}（{role}）可以在死前射杀一人!",
            # Config
            "config_loaded": "已加载配置文件：{config_path}",
            "preset_info": "预设组合：{preset}",
            "interface_mode": "界面模式：Console（自动执行）",
        },
    }

    def __init__(self, language: str = "en-US") -> None:
        """Initialize locale with specified language.

        Args:
            language: Language code (en-US, zh-TW, zh-CN).
        """
        if language not in self.MESSAGES:
            # Fallback to English if language not supported
            language = "en-US"
        self.language = language
        self.messages = self.MESSAGES[language]

    def get(self, key: str, **kwargs: str | int) -> str:
        """Get a localized message with optional formatting.

        Args:
            key: Message key.
            **kwargs: Format arguments for the message.

        Returns:
            str: Formatted localized message.
        """
        template = self.messages.get(key, key)
        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError:
                # If formatting fails, return template as-is
                return template
        return template

    def set_language(self, language: str) -> None:
        """Change the current language.

        Args:
            language: Language code (en-US, zh-TW, zh-CN).
        """
        if language in self.MESSAGES:
            self.language = language
            self.messages = self.MESSAGES[language]
