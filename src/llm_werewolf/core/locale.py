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
            # Narrator messages
            "narrator_night_falls": "🌙 Night falls, everyone close your eyes...",
            "narrator_werewolves_wake": "🐺 Werewolves, please open your eyes and discuss...",
            "narrator_werewolves_vote": "🐺 Werewolves, please vote for your target...",
            "narrator_werewolves_sleep": "🐺 Werewolves, close your eyes...",
            "narrator_daybreak": "☀️ The sun rises, everyone open your eyes...",
            # Role actions
            "role_acting": "🎬 {role} ({player}) is acting...",
            "player_speech": "{player}: {speech}",
            "werewolf_discussion": "🐺 {player} (Werewolf): {speech}",
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
            # Sheriff Election
            "sheriff_campaign_started": "Sheriff election begins. Players may volunteer to campaign for sheriff.",
            "no_candidates": "No one volunteered to campaign for sheriff. There will be no sheriff this game.",
            "player_volunteers": "{player} volunteers to campaign for sheriff.",
            "campaign_speeches_start": "{count} candidates will now give their campaign speeches.",
            "candidate_speech": "{candidate}'s speech: {speech}",
            "no_voters": "No non-candidate players available to vote. All players are candidates.",
            "sheriff_voting_start": "{count} non-candidate player(s) will now vote for sheriff.",
            "sheriff_vote_cast": "{voter} voted for {candidate}.",
            "sheriff_vote_abstained": "{voter} abstained from voting.",
            "sheriff_vote_result": "{candidate} received {votes} vote(s).",
            "sheriff_tie": "Tie between {candidates}. No sheriff this game.",
            "sheriff_elected": "{player} has been elected sheriff!",
            # Sheriff Badge Transfer
            "sheriff_died_transfer": "Sheriff {sheriff} has died. They may transfer the badge or tear it.",
            "sheriff_badge_torn": "{sheriff} tore the sheriff badge. There is no sheriff anymore.",
            "sheriff_badge_transferred": "{sheriff} transferred the sheriff badge to {target}.",
            # Other abilities
            "elder_penalty": "All villager abilities disabled due to Elder execution",
            "nightmare_blocked": "{player} ({role}) was blocked by Nightmare Wolf",
            "witch_uses_poison": "🧪 Witch used poison on {target}",
            "witch_poisoned_target": "{target} was poisoned by witch",
            # Error messages
            "speech_failed": "{player}: [Speech failed - {error}]",
            "discussion_failed": "{player}: [Discussion failed - {error}]",
            # Config
            "config_loaded": "Loaded configuration: {config_path}",
            "player_count_info": "Number of players: {num_players}",
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
            "alive_players": "\n存活玩家: ",
            "dead_players": "\n淘汰玩家: ",
            "player_role_info": "- {name}({role})",
            # Deaths
            "player_died": "{player} 死亡",
            "killed_by_werewolves": "{player} 被狼人殺害",
            "voted_out": "{player} 被投票淘汰",
            "player_eliminated": "{player} 被投票淘汰，身分是 {role}。",
            "died_of_heartbreak": "{player} 因愛而死(戀人)!",
            "died_from_charm": "{player} 被狼美人魅惑而死(狼美人 {wolf_beauty} 被淘汰)!",
            # Voting
            "vote_cast": "🗳️ {voter} 投票給 {target}",
            "vote_summary": "\n📊 投票統計: ",
            "vote_count": "  {target}: {count} 票 - {voters}",
            "vote_tied": "投票平手，無人被淘汰。",
            "no_votes": "無人投票。",
            # Narrator messages
            "narrator_night_falls": "🌙 天黑請閉眼...",
            "narrator_werewolves_wake": "🐺 狼人請睜眼，請討論並選擇目標...",
            "narrator_werewolves_vote": "🐺 狼人請投票...",
            "narrator_werewolves_sleep": "🐺 狼人請閉眼...",
            "narrator_daybreak": "☀️ 天亮了，所有人請睜眼...",
            # Role actions
            "role_acting": "🎬 {role}({player})正在行動...",
            "player_speech": "{player}: {speech}",
            "werewolf_discussion": "🐺 {player}(狼人): {speech}",
            "werewolf_voting": "🐺 狼人正在討論目標...",
            "werewolf_target": "🐺 狼人選擇了 {target}",
            "witch_saved": "💊 女巫救了 {target}",
            "witch_poisoned": "☠️ 女巫毒殺了 {target}",
            "guard_protected": "🛡️ 守衛保護了 {target}",
            "seer_checked": "🔮 預言家查驗了 {target}: {result}",
            "hunter_shoots": "🏹 獵人 {hunter} 射殺了 {target}",
            "alpha_wolf_shoots": "🐺👑 狼王 {alpha} 帶走了 {target}",
            "lovers_linked": "💕 戀人連結: {player1} 和 {player2}",
            "white_wolf_kills": "🐺⚪ 白狼王殺了 {target}",
            "wolf_beauty_charms": "🐺💋 狼美人魅惑了 {target}",
            "cupid_links": "💘 丘比特將 {player1} 和 {player2} 連結為戀人",
            # Special cases
            "idiot_revealed": "{player} 揭示自己是白癡，倖免於難!",
            "elder_executed": "長老被村民處決了!所有村民失去特殊能力作為懲罰!",
            "elder_attacked": "{player} 被攻擊但倖存(長老)!",
            "protected_by_guard": "{player} 被守衛保護了!",
            "saved_by_witch": "{player} 被女巫救了!",
            "poisoned_no_ability": "{player} 被女巫毒殺，無法使用死亡技能。",
            "death_ability_active": "{player}({role})可以在死前射殺一人!",
            # Sheriff Election
            "sheriff_campaign_started": "警長選舉開始，玩家可以自願競選警長。",
            "no_candidates": "沒有人自願競選警長，本局沒有警長。",
            "player_volunteers": "{player} 自願競選警長。",
            "campaign_speeches_start": "{count} 位候選人將發表競選演說。",
            "candidate_speech": "{candidate} 的演說: {speech}",
            "no_voters": "沒有非候選人可以投票，所有玩家都是候選人。",
            "sheriff_voting_start": "{count} 位非候選人將投票選舉警長。",
            "sheriff_vote_cast": "{voter} 投票給 {candidate}。",
            "sheriff_vote_abstained": "{voter} 棄權。",
            "sheriff_vote_result": "{candidate} 得到 {votes} 票。",
            "sheriff_tie": "{candidates} 平手，本局沒有警長。",
            "sheriff_elected": "{player} 當選警長!",
            # Sheriff Badge Transfer
            "sheriff_died_transfer": "警長 {sheriff} 已死亡，可以選擇移交或撕毀警徽。",
            "sheriff_badge_torn": "{sheriff} 撕毀了警徽，不再有警長。",
            "sheriff_badge_transferred": "{sheriff} 將警徽移交給 {target}。",
            # Other abilities
            "elder_penalty": "長老被處決，所有村民失去特殊能力",
            "nightmare_blocked": "{player}({role})被夢魘狼封印",
            "witch_uses_poison": "🧪 女巫對 {target} 使用毒藥",
            "witch_poisoned_target": "{target} 被女巫毒殺",
            # Error messages
            "speech_failed": "{player}: [發言失敗 - {error}]",
            "discussion_failed": "{player}: [討論失敗 - {error}]",
            # Config
            "config_loaded": "已載入設定檔: {config_path}",
            "player_count_info": "玩家人數: {num_players}",
            "interface_mode": "介面模式: Console(自動執行)",
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
            "alive_players": "\n存活玩家: ",
            "dead_players": "\n淘汰玩家: ",
            "player_role_info": "- {name}({role})",
            # Deaths
            "player_died": "{player} 死亡",
            "killed_by_werewolves": "{player} 被狼人杀害",
            "voted_out": "{player} 被投票淘汰",
            "player_eliminated": "{player} 被投票淘汰，身份是 {role}。",
            "died_of_heartbreak": "{player} 因爱而死(恋人)!",
            "died_from_charm": "{player} 被狼美人魅惑而死(狼美人 {wolf_beauty} 被淘汰)!",
            # Voting
            "vote_cast": "🗳️ {voter} 投票给 {target}",
            "vote_summary": "\n📊 投票统计: ",
            "vote_count": "  {target}: {count} 票 - {voters}",
            "vote_tied": "投票平手，无人被淘汰。",
            "no_votes": "无人投票。",
            # Narrator messages
            "narrator_night_falls": "🌙 天黑请闭眼...",
            "narrator_werewolves_wake": "🐺 狼人请睁眼，请讨论并选择目标...",
            "narrator_werewolves_vote": "🐺 狼人请投票...",
            "narrator_werewolves_sleep": "🐺 狼人请闭眼...",
            "narrator_daybreak": "☀️ 天亮了，所有人请睁眼...",
            # Role actions
            "role_acting": "🎬 {role}({player})正在行动...",
            "player_speech": "{player}: {speech}",
            "werewolf_discussion": "🐺 {player}(狼人): {speech}",
            "werewolf_voting": "🐺 狼人正在讨论目标...",
            "werewolf_target": "🐺 狼人选择了 {target}",
            "witch_saved": "💊 女巫救了 {target}",
            "witch_poisoned": "☠️ 女巫毒杀了 {target}",
            "guard_protected": "🛡️ 守卫保护了 {target}",
            "seer_checked": "🔮 预言家查验了 {target}: {result}",
            "hunter_shoots": "🏹 猎人 {hunter} 射杀了 {target}",
            "alpha_wolf_shoots": "🐺👑 狼王 {alpha} 带走了 {target}",
            "lovers_linked": "💕 恋人连结: {player1} 和 {player2}",
            "white_wolf_kills": "🐺⚪ 白狼王杀了 {target}",
            "wolf_beauty_charms": "🐺💋 狼美人魅惑了 {target}",
            "cupid_links": "💘 丘比特将 {player1} 和 {player2} 连结为恋人",
            # Special cases
            "idiot_revealed": "{player} 揭示自己是白痴，幸免于难!",
            "elder_executed": "长老被村民处决了!所有村民失去特殊能力作为惩罚!",
            "elder_attacked": "{player} 被攻击但幸存(长老)!",
            "protected_by_guard": "{player} 被守卫保护了!",
            "saved_by_witch": "{player} 被女巫救了!",
            "poisoned_no_ability": "{player} 被女巫毒杀，无法使用死亡技能。",
            "death_ability_active": "{player}({role})可以在死前射杀一人!",
            # Sheriff Election
            "sheriff_campaign_started": "警长选举开始，玩家可以自愿竞选警长。",
            "no_candidates": "没有人自愿竞选警长，本局没有警长。",
            "player_volunteers": "{player} 自愿竞选警长。",
            "campaign_speeches_start": "{count} 位候选人将发表竞选演说。",
            "candidate_speech": "{candidate} 的演说: {speech}",
            "no_voters": "没有非候选人可以投票，所有玩家都是候选人。",
            "sheriff_voting_start": "{count} 位非候选人将投票选举警长。",
            "sheriff_vote_cast": "{voter} 投票给 {candidate}。",
            "sheriff_vote_abstained": "{voter} 弃权。",
            "sheriff_vote_result": "{candidate} 得到 {votes} 票。",
            "sheriff_tie": "{candidates} 平手，本局没有警长。",
            "sheriff_elected": "{player} 当选警长!",
            # Sheriff Badge Transfer
            "sheriff_died_transfer": "警长 {sheriff} 已死亡，可以选择移交或撕毁警徽。",
            "sheriff_badge_torn": "{sheriff} 撕毁了警徽，不再有警长。",
            "sheriff_badge_transferred": "{sheriff} 将警徽移交给 {target}。",
            # Other abilities
            "elder_penalty": "长老被处决，所有村民失去特殊能力",
            "nightmare_blocked": "{player}({role})被梦魇狼封印",
            "witch_uses_poison": "🧪 女巫对 {target} 使用毒药",
            "witch_poisoned_target": "{target} 被女巫毒杀",
            # Error messages
            "speech_failed": "{player}: [发言失败 - {error}]",
            "discussion_failed": "{player}: [讨论失败 - {error}]",
            # Config
            "config_loaded": "已加载配置文件: {config_path}",
            "player_count_info": "玩家人数: {num_players}",
            "interface_mode": "界面模式: Console(自动执行)",
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
