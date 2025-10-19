from llm_werewolf.core.roles.base import Camp, Role, RoleConfig, ActionPriority


class Thief(Role):
    """Thief role.

    On the first night, can choose between two randomly dealt role cards.
    The role they choose becomes their actual role for the game.
    """

    def __init__(self) -> None:
        """Initialize the Thief role."""
        super().__init__()
        self.available_roles: list[Role] = []
        self.has_chosen = False

    def get_config(self) -> RoleConfig:
        """Get configuration for the Thief role."""
        return RoleConfig(
            name="Thief",
            camp=Camp.NEUTRAL,  # Starts neutral, becomes whatever role they choose
            description=(
                "You are the Thief. On the first night, you are shown two extra role cards "
                "that were not dealt to other players. You must choose one of these roles "
                "to play for the rest of the game. Choose wisely!"
            ),
            priority=ActionPriority.THIEF,
            can_act_night=True,
            can_act_day=False,
            max_uses=1,
        )


class Lover(Role):
    """Lover role (created by Cupid).

    This is not a starting role but a status given by Cupid.
    Lovers win together and die together.
    """

    def __init__(self) -> None:
        """Initialize the Lover role."""
        super().__init__()
        self.partner_id: str | None = None
        self.original_role: Role | None = None

    def get_config(self) -> RoleConfig:
        """Get configuration for the Lover role.

        Note: Lover is a status/modifier, not a primary role.
        Players keep their original role but gain the lover status.
        """
        return RoleConfig(
            name="Lover",
            camp=Camp.NEUTRAL,  # Lovers form their own win condition
            description=(
                "You have been chosen as a Lover by Cupid. You share a special bond with another "
                "player. You both know each other's identities. If your partner dies, you will "
                "die immediately from heartbreak. Your goal is to survive together with your lover, "
                "even if it means going against your original camp."
            ),
            priority=None,
            can_act_night=False,
            can_act_day=False,
        )


class WhiteLoverWolf(Role):
    """White Lover Wolf - Special case.

    When a werewolf and a villager become lovers, they form a unique alliance.
    This is a dynamic role that represents the conflicted state.
    """

    def get_config(self) -> RoleConfig:
        """Get configuration for the White Lover Wolf role."""
        return RoleConfig(
            name="White Lover Wolf",
            camp=Camp.NEUTRAL,
            description=(
                "You are in a unique situation: you (or your lover) are a werewolf, "
                "and your lover (or you) are a villager. You must work together to eliminate "
                "all other players so that only you two remain. This is an extremely challenging "
                "victory condition, but if achieved, you both win together."
            ),
            priority=None,
            can_act_night=False,
            can_act_day=False,
        )
