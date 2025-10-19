from llm_werewolf.core.roles.base import ActionPriority, Camp, Role, RoleConfig
from llm_werewolf.core.roles.neutral import Lover, Thief, WhiteLoverWolf
from llm_werewolf.core.roles.villager import (
    Cupid,
    Elder,
    GraveyardKeeper,
    Guard,
    Hunter,
    Idiot,
    Knight,
    Magician,
    Raven,
    Seer,
    Villager,
    Witch,
)
from llm_werewolf.core.roles.werewolf import (
    AlphaWolf,
    BloodMoonApostle,
    GuardianWolf,
    HiddenWolf,
    NightmareWolf,
    Werewolf,
    WhiteWolf,
    WolfBeauty,
)

__all__ = [
    # Base classes and enums
    "Role",
    "RoleConfig",
    "Camp",
    "ActionPriority",
    # Werewolf roles
    "Werewolf",
    "AlphaWolf",
    "WhiteWolf",
    "WolfBeauty",
    "GuardianWolf",
    "HiddenWolf",
    "BloodMoonApostle",
    "NightmareWolf",
    # Villager roles
    "Villager",
    "Seer",
    "Witch",
    "Hunter",
    "Guard",
    "Idiot",
    "Elder",
    "Knight",
    "Magician",
    "Cupid",
    "Raven",
    "GraveyardKeeper",
    # Neutral roles
    "Thief",
    "Lover",
    "WhiteLoverWolf",
]
