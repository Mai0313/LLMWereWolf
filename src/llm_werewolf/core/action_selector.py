import re
import random
from typing import TYPE_CHECKING

from llm_werewolf.ai import AgentType

if TYPE_CHECKING:
    from llm_werewolf.core.player import Player


class ActionSelector:
    """Helper class to get structured action selections from AI agents."""

    @staticmethod
    def build_target_selection_prompt(
        role_name: str,
        action_description: str,
        possible_targets: list["Player"],
        allow_skip: bool = False,
        additional_context: str = "",
    ) -> str:
        """Build a prompt for selecting a target player.

        Args:
            role_name: Name of the role performing the action.
            action_description: Description of what action to perform.
            possible_targets: List of possible target players.
            allow_skip: Whether the player can skip this action.
            additional_context: Additional context information.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [f"You are a {role_name}.", f"Action: {action_description}", ""]

        if additional_context:
            prompt_parts.append(additional_context)
            prompt_parts.append("")

        prompt_parts.append("Available targets:")
        for idx, target in enumerate(possible_targets, 1):
            prompt_parts.append(f"{idx}. {target.name} (Player ID: {target.player_id})")

        if allow_skip:
            prompt_parts.append(f"{len(possible_targets) + 1}. SKIP (do not perform this action)")

        prompt_parts.extend([
            "",
            "Please select a target by responding with ONLY the number (1, 2, 3, etc.).",
            "Do not include any other text in your response.",
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def parse_target_selection(
        response: str, possible_targets: list["Player"], allow_skip: bool = False
    ) -> "Player | None":
        """Parse AI response to extract selected target.

        Args:
            response: The AI's response.
            possible_targets: List of possible targets.
            allow_skip: Whether skipping was allowed.

        Returns:
            Player | None: The selected player, or None if skipped/invalid.
        """
        # Extract number from response
        numbers = re.findall(r"\d+", response.strip())
        if not numbers:
            return None

        try:
            selection = int(numbers[0])
            # Check if it's a valid selection
            if 1 <= selection <= len(possible_targets):
                return possible_targets[selection - 1]
            if allow_skip and selection == len(possible_targets) + 1:
                return None
        except (ValueError, IndexError):
            pass

        return None

    @staticmethod
    def build_yes_no_prompt(role_name: str, question: str, context: str = "") -> str:
        """Build a yes/no question prompt.

        Args:
            role_name: Name of the role.
            question: The question to ask.
            context: Additional context.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [f"You are a {role_name}.", f"Question: {question}"]

        if context:
            prompt_parts.append("")
            prompt_parts.append(context)

        prompt_parts.extend([
            "",
            "Please respond with ONLY 'YES' or 'NO'.",
            "Do not include any other text in your response.",
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def parse_yes_no(response: str) -> bool:
        """Parse yes/no response.

        Args:
            response: The AI's response.

        Returns:
            bool: True for yes, False for no.
        """
        response_lower = response.strip().lower()
        return "yes" in response_lower or "是" in response_lower

    @staticmethod
    def build_multi_target_prompt(
        role_name: str,
        action_description: str,
        possible_targets: list["Player"],
        num_targets: int,
        additional_context: str = "",
    ) -> str:
        """Build a prompt for selecting multiple targets.

        Args:
            role_name: Name of the role.
            action_description: Description of the action.
            possible_targets: List of possible targets.
            num_targets: Number of targets to select.
            additional_context: Additional context.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [
            f"You are a {role_name}.",
            f"Action: {action_description}",
            f"You need to select {num_targets} different targets.",
            "",
        ]

        if additional_context:
            prompt_parts.append(additional_context)
            prompt_parts.append("")

        prompt_parts.append("Available targets:")
        for idx, target in enumerate(possible_targets, 1):
            prompt_parts.append(f"{idx}. {target.name} (Player ID: {target.player_id})")

        prompt_parts.extend([
            "",
            f"Please select {num_targets} targets by responding with the numbers separated by commas.",
            "Example: 1, 3 (to select the 1st and 3rd targets)",
            "Do not include any other text in your response.",
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def parse_multi_target_selection(
        response: str, possible_targets: list["Player"], num_targets: int
    ) -> list["Player"] | None:
        """Parse multi-target selection response.

        Args:
            response: The AI's response.
            possible_targets: List of possible targets.
            num_targets: Expected number of targets.

        Returns:
            list[Player] | None: Selected players, or None if invalid.
        """
        numbers = re.findall(r"\d+", response.strip())
        if len(numbers) != num_targets:
            return None

        try:
            selected = []
            for num_str in numbers:
                selection = int(num_str)
                if 1 <= selection <= len(possible_targets):
                    selected.append(possible_targets[selection - 1])
                else:
                    return None

            # Check for duplicates
            if len(selected) != len({p.player_id for p in selected}):
                return None

            return selected
        except (ValueError, IndexError):
            return None

    @staticmethod
    def get_target_from_agent(
        agent: AgentType,
        role_name: str,
        action_description: str,
        possible_targets: list["Player"],
        allow_skip: bool = False,
        additional_context: str = "",
        fallback_random: bool = True,
    ) -> "Player | None":
        """Get a target selection from an AI agent.

        Args:
            agent: The AI agent.
            role_name: Name of the role.
            action_description: Description of the action.
            possible_targets: List of possible targets.
            allow_skip: Whether skipping is allowed.
            additional_context: Additional context.
            fallback_random: If True, randomly select if AI fails.

        Returns:
            Player | None: Selected target, or None if skipped.
        """
        if not possible_targets:
            return None

        prompt = ActionSelector.build_target_selection_prompt(
            role_name, action_description, possible_targets, allow_skip, additional_context
        )

        try:
            response = agent.get_response(prompt)
            target = ActionSelector.parse_target_selection(response, possible_targets, allow_skip)

            if target is not None or allow_skip:
                return target

            # If parsing failed and fallback is enabled
            if fallback_random:
                return random.choice(possible_targets)  # noqa: S311

        except Exception:
            # If agent fails and fallback is enabled
            if fallback_random:
                return random.choice(possible_targets)  # noqa: S311

        return None
