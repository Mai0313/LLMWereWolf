import re
import random

from llm_werewolf.core.types import AgentProtocol, PlayerProtocol


class ActionSelector:
    """Helper class to get structured action selections from AI agents."""

    @staticmethod
    def build_target_selection_prompt(
        role_name: str,
        action_description: str,
        possible_targets: list[PlayerProtocol],
        allow_skip: bool = False,
        additional_context: str = "",
        round_number: int | None = None,
        phase: str | None = None,
    ) -> str:
        """Build a prompt for selecting a target player.

        Args:
            role_name: Name of the role performing the action.
            action_description: Description of what action to perform.
            possible_targets: List of possible target players.
            allow_skip: Whether the player can skip this action.
            additional_context: Additional context information.
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [f"You are a {role_name}."]

        # Add round and phase information
        if round_number is not None and phase:
            prompt_parts.append(f"Current: Round {round_number} - {phase}")
        elif round_number is not None:
            prompt_parts.append(f"Current Round: {round_number}")

        prompt_parts.extend([f"Action: {action_description}", ""])

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
        response: str, possible_targets: list[PlayerProtocol], allow_skip: bool = False
    ) -> PlayerProtocol | None:
        """Parse AI response to extract selected target.

        Args:
            response: The AI's response.
            possible_targets: List of possible targets.
            allow_skip: Whether skipping was allowed.

        Returns:
            PlayerProtocol | None: The selected player, or None if skipped/invalid.
        """
        numbers = re.findall(r"\d+", response.strip())
        if not numbers:
            return None

        try:
            selection = int(numbers[0])
            if 1 <= selection <= len(possible_targets):
                return possible_targets[selection - 1]
            if allow_skip and selection == len(possible_targets) + 1:
                return None
        except (ValueError, IndexError):
            pass

        return None

    @staticmethod
    def build_yes_no_prompt(
        role_name: str,
        question: str,
        context: str = "",
        round_number: int | None = None,
        phase: str | None = None,
    ) -> str:
        """Build a yes/no question prompt.

        Args:
            role_name: Name of the role.
            question: The question to ask.
            context: Additional context.
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [f"You are a {role_name}."]

        # Add round and phase information
        if round_number is not None and phase:
            prompt_parts.append(f"Current: Round {round_number} - {phase}")
        elif round_number is not None:
            prompt_parts.append(f"Current Round: {round_number}")

        prompt_parts.append(f"Question: {question}")

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
        possible_targets: list[PlayerProtocol],
        num_targets: int,
        additional_context: str = "",
        round_number: int | None = None,
        phase: str | None = None,
    ) -> str:
        """Build a prompt for selecting multiple targets.

        Args:
            role_name: Name of the role.
            action_description: Description of the action.
            possible_targets: List of possible targets.
            num_targets: Number of targets to select.
            additional_context: Additional context.
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            str: The formatted prompt.
        """
        prompt_parts = [f"You are a {role_name}."]

        # Add round and phase information
        if round_number is not None and phase:
            prompt_parts.append(f"Current: Round {round_number} - {phase}")
        elif round_number is not None:
            prompt_parts.append(f"Current Round: {round_number}")

        prompt_parts.extend([
            f"Action: {action_description}",
            f"You need to select {num_targets} different targets.",
            "",
        ])

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
        response: str, possible_targets: list[PlayerProtocol], num_targets: int
    ) -> list[PlayerProtocol] | None:
        """Parse multi-target selection response.

        Args:
            response: The AI's response.
            possible_targets: List of possible targets.
            num_targets: Expected number of targets.

        Returns:
            list[PlayerProtocol] | None: Selected players, or None if invalid.
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

            if len(selected) != len({p.player_id for p in selected}):
                return None

            return selected
        except (ValueError, IndexError):
            return None

    @staticmethod
    def get_target_from_agent(
        agent: AgentProtocol,
        role_name: str,
        action_description: str,
        possible_targets: list[PlayerProtocol],
        allow_skip: bool = False,
        additional_context: str = "",
        fallback_random: bool = True,
        round_number: int | None = None,
        phase: str | None = None,
    ) -> PlayerProtocol | None:
        """Get a target selection from an AI agent.

        Args:
            agent: The AI agent.
            role_name: Name of the role.
            action_description: Description of the action.
            possible_targets: List of possible targets.
            allow_skip: Whether skipping is allowed.
            additional_context: Additional context.
            fallback_random: If True, randomly select if AI fails.
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            PlayerProtocol | None: Selected target, or None if skipped.
        """
        if not possible_targets:
            return None

        prompt = ActionSelector.build_target_selection_prompt(
            role_name,
            action_description,
            possible_targets,
            allow_skip,
            additional_context,
            round_number,
            phase,
        )

        try:
            response = agent.get_response(prompt)
            target = ActionSelector.parse_target_selection(response, possible_targets, allow_skip)

            if target is not None or allow_skip:
                return target

            if fallback_random:
                return random.choice(possible_targets)  # noqa: S311

        except Exception:
            if fallback_random:
                return random.choice(possible_targets)  # noqa: S311

        return None

    @staticmethod
    def ask_yes_no(
        agent: AgentProtocol,
        context: str,
        question: str,
        role_name: str = "",
        round_number: int | None = None,
        phase: str | None = None,
    ) -> bool:
        """Ask an agent a yes/no question.

        Args:
            agent: The AI agent.
            context: Additional context for the question.
            question: The yes/no question to ask.
            role_name: Name of the role (optional, can be extracted from context).
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            bool: True for yes, False for no.
        """
        if not role_name:
            role_name = "Player"

        prompt = ActionSelector.build_yes_no_prompt(
            role_name, question, context, round_number, phase
        )

        try:
            response = agent.get_response(prompt)
            return ActionSelector.parse_yes_no(response)
        except Exception:
            return False

    @staticmethod
    def select_target(
        agent: AgentProtocol,
        context: str,
        possible_targets: list[PlayerProtocol],
        action_description: str,
        role_name: str = "",
        allow_skip: bool = False,
        fallback_random: bool = True,
        round_number: int | None = None,
        phase: str | None = None,
    ) -> PlayerProtocol | None:
        """Select a target from a list of possible targets.

        Args:
            agent: The AI agent.
            context: Additional context for the selection.
            possible_targets: List of possible targets.
            action_description: Description of the action.
            role_name: Name of the role (optional).
            allow_skip: Whether skipping is allowed.
            fallback_random: If True, randomly select if AI fails.
            round_number: Current round number.
            phase: Current game phase.

        Returns:
            PlayerProtocol | None: Selected target, or None if skipped.
        """
        if not role_name:
            role_name = "Player"

        return ActionSelector.get_target_from_agent(
            agent,
            role_name,
            action_description,
            possible_targets,
            allow_skip,
            context,
            fallback_random,
            round_number,
            phase,
        )

    @staticmethod
    def get_free_response(agent: AgentProtocol, context: str, prompt: str) -> str:
        """Get a free-form text response from an agent.

        Args:
            agent: The AI agent.
            context: Context information.
            prompt: The prompt/question to ask.

        Returns:
            str: The agent's response.
        """
        full_prompt = f"{context}\n\n{prompt}"
        try:
            return agent.get_response(full_prompt)
        except Exception:
            return ""
