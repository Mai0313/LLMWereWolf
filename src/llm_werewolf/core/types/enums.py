from enum import Enum


class Camp(str, Enum):
    """Enum representing the different camps in the game."""

    WEREWOLF = "werewolf"
    VILLAGER = "villager"
    NEUTRAL = "neutral"


class ActionPriority(int, Enum):
    """Enum representing the priority order of night actions."""

    CUPID = 100
    THIEF = 95
    GUARD = 90
    WEREWOLF = 80
    WHITE_WOLF = 75
    WITCH = 70
    SEER = 60
    GRAVEYARD_KEEPER = 50
    RAVEN = 40


class GamePhase(str, Enum):
    """Enum representing the different phases of the game."""

    SETUP = "setup"
    NIGHT = "night"
    DAY_DISCUSSION = "day_discussion"
    DAY_VOTING = "day_voting"
    ENDED = "ended"


class PlayerStatus(str, Enum):
    """Enum representing special statuses a player can have."""

    ALIVE = "alive"
    DEAD = "dead"
    PROTECTED = "protected"
    POISONED = "poisoned"
    SAVED = "saved"
    CHARMED = "charmed"
    BLOCKED = "blocked"
    MARKED = "marked"
    REVEALED = "revealed"
    NO_VOTE = "no_vote"
    LOVER = "lover"


class ActionType(str, Enum):
    """Enum representing different types of actions."""

    WEREWOLF_KILL = "werewolf_kill"
    WITCH_SAVE = "witch_save"
    WITCH_POISON = "witch_poison"
    SEER_CHECK = "seer_check"
    GUARD_PROTECT = "guard_protect"
    CUPID_LINK = "cupid_link"
    RAVEN_MARK = "raven_mark"
    WHITE_WOLF_KILL = "white_wolf_kill"
    WOLF_BEAUTY_CHARM = "wolf_beauty_charm"
    NIGHTMARE_BLOCK = "nightmare_block"

    VOTE = "vote"
    HUNTER_SHOOT = "hunter_shoot"
    KNIGHT_DUEL = "knight_duel"
    ALPHA_WOLF_SHOOT = "alpha_wolf_shoot"

    THIEF_CHOOSE = "thief_choose"
    MAGICIAN_SWAP = "magician_swap"


class EventType(str, Enum):
    """Enum representing different types of game events."""

    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    PHASE_CHANGED = "phase_changed"
    ROUND_STARTED = "round_started"

    PLAYER_DIED = "player_died"
    PLAYER_REVIVED = "player_revived"
    ROLE_REVEALED = "role_revealed"
    ROLE_ACTING = "role_acting"

    WEREWOLF_KILLED = "werewolf_killed"
    WITCH_SAVED = "witch_saved"
    WITCH_POISONED = "witch_poisoned"
    SEER_CHECKED = "seer_checked"
    GUARD_PROTECTED = "guard_protected"

    VOTE_CAST = "vote_cast"
    VOTE_RESULT = "vote_result"
    PLAYER_ELIMINATED = "player_eliminated"

    LOVERS_LINKED = "lovers_linked"
    LOVER_DIED = "lover_died"
    HUNTER_REVENGE = "hunter_revenge"
    KNIGHT_DUEL = "knight_duel"

    PLAYER_SPEECH = "player_speech"
    PLAYER_DISCUSSION = "player_discussion"

    MESSAGE = "message"
    ERROR = "error"
