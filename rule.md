# LLM WereWolf - Game Rules (Code Implementation · Final Consolidated Edition)

This document catalogs **the actual implementation of every game rule in the codebase**. Each rule has been verified against the source code.

---

## Table of Contents

- [1. Game Setup](#1-game-setup)
- [2. Camps](#2-camps)
- [3. Game Phases and Flow](#3-game-phases-and-flow)
- [4. Night Phase](#4-night-phase)
- [5. Day Phase](#5-day-phase)
- [6. Voting Phase](#6-voting-phase)
- [7. Sheriff System](#7-sheriff-system)
- [8. Roles - Villager Camp](#8-roles---villager-camp)
- [9. Roles - Werewolf Camp](#9-roles---werewolf-camp)
- [10. Roles - Neutral Camp](#10-roles---neutral-camp)
- [11. Victory Conditions](#11-victory-conditions)
- [12. Death Resolution](#12-death-resolution)
- [13. Special Mechanics](#13-special-mechanics)
- [14. Preset Role Compositions](#14-preset-role-compositions)
- [15. Timeout Settings](#15-timeout-settings)
- [Appendix: Role Summary Table](#appendix-role-summary-table)

---

## 1. Game Setup

| Rule | Source |
|------|--------|
| Minimum 6 players, maximum 20 players | `config/presets.py`, `config/game_config.py` |
| The number of roles must exactly match the number of players | `config/game_config.py` |
| At least one werewolf role is required | `role_registry.py` |
| Roles are randomly shuffled before assignment | `engine/base.py` |
| Each player is assigned exactly one role | `engine/base.py` |

---

## 2. Camps

| Camp | Code Value | Description |
|------|------------|-------------|
| **Werewolf Camp** | `werewolf` | Goal: make the number of werewolves greater than or equal to the number of villagers |
| **Villager Camp** | `villager` | Goal: eliminate all werewolves |
| **Neutral Camp** | `neutral` | Independent win conditions (Lovers, Thief, etc.) |

Source: `types/enums.py` - `Camp`

---

## 3. Game Phases and Flow

### Phase Order

```
SETUP → NIGHT → [SHERIFF_ELECTION*] → DAY_DISCUSSION → DAY_VOTING → NIGHT → ...
```

> *The sheriff election occurs only once, after the first night.

### Phase Transition Rules

| From | To | Condition |
|------|----|-----------|
| SETUP | NIGHT | The game starts and `round_number` is set to 1 |
| NIGHT | SHERIFF_ELECTION | Round 1, and the sheriff election has not yet been held |
| NIGHT | DAY_DISCUSSION | Round > 1, or the sheriff election has already finished |
| SHERIFF_ELECTION | DAY_DISCUSSION | The election ends |
| DAY_DISCUSSION | DAY_VOTING | The discussion ends |
| DAY_VOTING | NIGHT | Voting ends, and `round_number + 1` |

Source: `game_state.py` - `next_phase()`

### Per-Round State Reset

When transitioning from DAY_VOTING back to NIGHT, the following state is cleared:

- `night_deaths`, `day_deaths`, `death_abilities_used`, `death_causes`
- `votes` (daytime votes)
- `werewolf_target`, `werewolf_votes`
- `witch_saved_target`, `witch_poison_target`
- `guard_protected`, `guardian_wolf_protected`
- `nightmare_blocked`, `raven_marked`

Source: `game_state.py` - `next_phase()`, `reset_deaths()`

### When Victory Is Checked

Victory conditions are checked at the following points:
1. After the night phase ends (after death resolution)
2. After the sheriff election
3. After the voting phase ends (after exile resolution)

If a winner is detected at any of these points, the game ends immediately.

Source: `engine/base.py` - `play_game()`

---

## 4. Night Phase

### Night Action Priority Order

Actions are executed in **descending priority order** (higher numbers act first):

| Order | Priority | Role |
|------|----------|------|
| 1 | 100 | **Cupid** (first night only) |
| 2 | 98 | **Nightmare Wolf** (ability block) |
| 3 | 95 | **Thief** (first night only; not currently implemented) |
| 4 | 90 | **Guard** / **Guardian Wolf** |
| 5 | 80 | **Werewolf** (all werewolf roles vote collectively) |
| 6 | 75 | **White Wolf** (extra kill) |
| 7 | 70 | **Witch** (antidote / poison) |
| 8 | 60 | **Seer** |
| 9 | 50 | **Graveyard Keeper** |
| 10 | 40 | **Raven** |

Source: `types/enums.py` - `ActionPriority`, `engine/action_processor.py`

### Werewolf Discussion and Voting

1. If multiple werewolves are alive, they first hold an **internal discussion**, with each werewolf sharing an opinion.
2. Each werewolf then casts an **individual vote** for one non-werewolf target.
3. The player with the **most votes** becomes the kill target.
4. **Tie handling**: if multiple targets are tied, **one is chosen at random**.
5. Werewolves may only target **living non-werewolf** players.

Source: `engine/night_phase.py` - `_run_werewolf_discussion()`, `_resolve_werewolf_votes()`

### Nightmare Wolf Blocking Mechanic

- The Nightmare Wolf may block one player's ability each night.
- For a blocked player, `has_night_action()` returns `False`, and their action is skipped in `process_actions()`.
- The Nightmare Wolf's own blocking action **cannot itself be blocked**.
- The block target may be any living player except the Nightmare Wolf.

Source: `roles/base.py` - `has_night_action()`, `engine/action_processor.py` - `_is_actor_blocked()`

### Night Death Resolution Order

After all night actions have been processed:

1. **Werewolf kill resolution** (checked in order: Witch antidote -> Guard protection -> Elder extra life -> otherwise death)
2. **Witch poison resolution**
3. **Wolf Beauty charm chain** (if Wolf Beauty dies that night, the charmed target dies as well)
4. **Death-triggered abilities** (Sheriff badge transfer -> Hunter / Alpha Wolf shooting)

> Note: lovers' suicide is triggered immediately whenever each individual death event occurs, including inside steps 1 and 2. It is not a separate step.

Source: `engine/death_handler.py` - `resolve_deaths()`

---

## 5. Day Phase

### Discussion Phase Rules

1. **All living players** speak in sequence, one at a time.
2. Each player receives the following information:
   - their own role
   - the list of players who died last night, or a peaceful night message if no one died
   - the list of living players
   - their own action history
   - the full public discussion history from previous rounds
3. Each player gives a **1-3 sentence** statement.
4. All statements are added to the **public discussion history** and are visible to everyone.

Source: `engine/day_phase.py` - `run_day_phase()`, `_build_discussion_context()`

---

## 6. Voting Phase

### Voting Rules

| Rule | Details |
|------|---------|
| Who can vote | All living players with voting rights (`can_vote() == True`) |
| Valid targets | Any living player (**cannot vote for yourself**) |
| Vote weight | Normal player = **1.0**, Sheriff = **1.5** |
| Raven mark | A marked player receives an extra **+1 vote** |
| Exile rule | The player with the **most votes** is exiled |
| Tie handling | **No one is exiled** |
| Idiot exception | The Idiot reveals their identity, **does not die**, but permanently loses voting rights |
| Elder exception | If the Elder is exiled by vote -> **all Villager Camp special abilities are permanently disabled** |

Source: `engine/voting_phase.py`, `game_state.py` - `get_vote_counts()`, `player.py` - `get_vote_weight()`

### Post-Exile Chain Reactions (Daytime)

After a player is exiled by vote, the following are processed in order:
1. Check the **Elder penalty** (all villager abilities become disabled)
2. Check **lovers' suicide** (the partner dies of heartbreak)
3. Check the **Wolf Beauty charm chain** (the charmed target dies as well)
4. Process **death-triggered abilities** (Sheriff badge transfer -> Hunter / Alpha Wolf shooting)

Source: `engine/voting_phase.py` - `_eliminate_voted_player()`, `run_voting_phase()`

---

## 7. Sheriff System

### Election Flow (Round 1 Only)

1. **Candidacy**: all living players are asked whether they want to run for Sheriff.
2. **Automatic election**: if there is only 1 candidate, that player wins automatically.
3. **Speech**: each candidate gives a 2-3 sentence campaign speech.
4. **Voting**: all living players vote for one candidate. Abstaining is allowed, and players cannot vote for themselves.
5. **Result**:
   - A single top vote-getter -> becomes Sheriff
   - A tie -> **no one is elected**

Source: `engine/sheriff_election.py`

### Sheriff Privileges

| Privilege | Details |
|-----------|---------|
| Weighted vote | **1.5x** vote weight (normal players have 1.0) |
| Badge transfer | Upon death, the Sheriff may transfer the badge to a living player |
| Destroy badge | Upon death, the Sheriff may destroy the badge, leaving no Sheriff afterward |

Source: `player.py` - `get_vote_weight()`, `engine/death_handler.py` - `_handle_sheriff_badge_transfer()`

### Sheriff Death Handling

When the Sheriff dies:
1. The Sheriff's agent is asked to **choose one living player** to receive the badge.
2. Or it may choose to **skip** (destroy the badge, with `allow_skip=True`).
3. If there are no living players or no agent, the badge is destroyed automatically.

Source: `engine/death_handler.py` - `_handle_sheriff_badge_transfer()`

---

## 8. Roles - Villager Camp

### Villager

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | None |
| Day Action | None |
| Special | No special abilities; can only participate in daytime voting |

### Seer

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Check the camp identity of one living player |
| Priority | 60 |
| Target | Any living player (cannot check self) |
| Special | Hidden Wolf appears as **Villager**; an untransformed Blood Moon Apostle appears as **Villager**; a transformed Blood Moon Apostle appears as **Werewolf** |

Check results are stored by round in `game_state.seer_checked`.

Source: `roles/villager.py` - `Seer`, `actions/villager.py` - `SeerCheckAction`

### Witch

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Antidote and/or poison |
| Priority | 70 |
| Antidote | Save the target selected for the werewolf kill; **usable once per game** |
| Poison | Poison any living player (cannot poison self); **usable once per game** |
| Restriction | **Cannot use both potions on the same night** |

The Witch is informed of the werewolves' kill target before deciding whether to use the antidote.

Source: `roles/villager.py` - `Witch`, `actions/villager.py` - `WitchSaveAction`, `WitchPoisonAction`

### Hunter

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | None |
| Day Action | Death-triggered ability (shoot) |
| Trigger | When killed by werewolves **or** exiled by vote |
| Uses | **Once** |
| Restriction | If the cause of death is **Witch poison**, the shooting ability **cannot** be used |

Source: `roles/villager.py` - `Hunter`, `engine/death_handler.py` - `_handle_death_abilities()`

### Guard

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Protect one living player from the werewolf kill |
| Priority | 90 |
| Restriction | **Cannot protect the same player on two consecutive nights** |
| Self-Protection | Allowed (self is included in the target list) |

Source: `roles/villager.py` - `Guard`, `actions/villager.py` - `GuardProtectAction`

### Idiot

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | None |
| Day Action | None |
| Special | If **exiled by vote**: reveals identity, **does not die**, but **permanently loses voting rights** |
| Note | After revealing, the Idiot can still be killed by werewolves at night |

Source: `roles/villager.py` - `Idiot`, `engine/voting_phase.py` - `_eliminate_voted_player()`

### Elder

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | None |
| Lives | **2** (can survive one werewolf attack) |
| Penalty | If exiled by vote -> **all Villager Camp special abilities are permanently disabled** (`role.disabled = True`) |

Source: `roles/villager.py` - `Elder`, `engine/death_handler.py` - `_handle_elder_penalty()`, `_handle_werewolf_kill()`

### Knight

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | None |
| Day Action | Challenge one player to a duel |
| Uses | **Once per game** |
| Duel Result | If the target is a werewolf -> **the target dies**; if the target is not a werewolf -> **the Knight dies** |

Source: `roles/villager.py` - `Knight`, `actions/villager.py` - `KnightDuelAction`

### Magician (Not Implemented)

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Swap the roles of two players (placeholder) |
| Priority | 90 (same as Guard) |
| Uses | **Once per game** |
| Status | **Not implemented** - currently returns an empty action list |

Source: `roles/villager.py` - `Magician`

### Cupid

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Link two players as lovers (**first night only**) |
| Priority | 100 (highest) |
| Uses | **Once** |
| Effect | The linked players become lovers; when one dies, the other immediately dies of heartbreak |

Source: `roles/villager.py` - `Cupid`, `actions/villager.py` - `CupidLinkAction`

### Raven

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Mark (curse) one living player |
| Priority | 40 |
| Effect | The marked player receives an extra **+1 vote** in the next day's vote |
| Reset | The mark is **cleared every round** |

Source: `roles/villager.py` - `Raven`, `actions/villager.py` - `RavenMarkAction`, `game_state.py` - `get_vote_counts()`

### Graveyard Keeper

| Attribute | Value |
|-----------|-------|
| Camp | Villager |
| Night Action | Check the role and camp of one **dead** player |
| Priority | 50 |
| Target | Dead players only |
| Can Skip | Yes |

Source: `roles/villager.py` - `GraveyardKeeper`, `actions/villager.py` - `GraveyardKeeperCheckAction`

---

## 9. Roles - Werewolf Camp

> All werewolf roles, except an untransformed Blood Moon Apostle, participate in the **collective werewolf vote** every night. Werewolves may only target **living non-werewolf** players.

### Werewolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote to kill villagers |
| Priority | 80 |
| Special | None - standard werewolf |

### Alpha Wolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote |
| Priority | 80 |
| Death Ability | Upon death, may **shoot and take down** one living player |
| Restriction | If the cause of death is **Witch poison**, the shooting ability **cannot** be used |

Source: `roles/werewolf.py` - `AlphaWolf`, `engine/death_handler.py` - `_handle_death_abilities()`

### White Wolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote + extra kill |
| Priority | 75 (extra kill) |
| Extra Kill | On **odd-numbered rounds** (Night 1, 3, 5, ...) may choose to kill **another werewolf** (can skip) |
| Can Be Defended | Guardian Wolf protection can block the White Wolf's extra kill |

Source: `roles/werewolf.py` - `WhiteWolf`, `actions/werewolf.py` - `WhiteWolfKillAction`

### Wolf Beauty

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote + charm |
| Priority | 80 |
| Charm | **Usable once per game**, charm one living player |
| Charm Effect | When Wolf Beauty **dies**, the charmed target **dies immediately as well** |

Source: `roles/werewolf.py` - `WolfBeauty`, `actions/werewolf.py` - `WolfBeautyCharmAction`, `engine/death_handler.py`

### Guardian Wolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote + protect one werewolf |
| Priority | 90 (same as Guard) |
| Protection | May protect one **werewolf** from death each night |
| Effect | Can defend against the **White Wolf's extra kill** |
| Can Skip | Yes |

Source: `roles/werewolf.py` - `GuardianWolf`, `actions/werewolf.py` - `GuardianWolfProtectAction`

### Hidden Wolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote |
| Priority | 80 |
| Special | Appears as **Villager** when checked by the Seer |

Source: `roles/werewolf.py` - `HiddenWolf`, `actions/villager.py` - `SeerCheckAction`

### Blood Moon Apostle

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Conditional (see below) |
| Priority | 80 (after transformation) |
| Initial State | Does **not** wake up with the werewolves and does **not** participate in the werewolf vote |
| Transformation Trigger | When all other standard werewolves, excluding other Blood Moon Apostles, are dead |
| After Transformation | Behaves like a standard werewolf and joins the werewolf vote |
| Seer Result | Appears as **Villager** before transformation and **Werewolf** after transformation |

**Special victory-condition rules:**
- **For werewolf victory checks**: an untransformed Blood Moon Apostle **does not count** toward the werewolf total when evaluating "werewolves >= villagers".
- **For villager victory checks**: a Blood Moon Apostle counts as a **werewolf** whether transformed or not, and must be eliminated for the villagers to win.
- **Winner list**: even if untransformed, it still wins **together with the Werewolf Camp**.

Source: `roles/werewolf.py` - `BloodMoonApostle`, `victory.py`

### Nightmare Wolf

| Attribute | Value |
|-----------|-------|
| Camp | Werewolf |
| Night Action | Participate in the werewolf vote + block one player's ability |
| Priority | 98 (second only to Cupid) |
| Block | Blocks one player's ability each night, preventing that player from using their role ability that night |
| Target | Any living player (cannot choose self) |
| Built-in Immunity | The Nightmare Wolf's own blocking action **cannot be blocked** |
| Can Skip | Yes |

Source: `roles/werewolf.py` - `NightmareWolf`, `actions/werewolf.py` - `NightmareWolfBlockAction`

---

## 10. Roles - Neutral Camp

### Thief (Not Implemented)

| Attribute | Value |
|-----------|-------|
| Camp | Neutral (changes based on the chosen role) |
| Night Action | Choose one of two extra role cards (first night only) |
| Priority | 95 |
| Uses | **Once** |
| Status | **Not implemented** - currently returns an empty action list |

Source: `roles/neutral.py` - `Thief`

### Lover (Dynamic State)

| Attribute | Value |
|-----------|-------|
| Camp | Neutral |
| Source | Created by Cupid |
| Night Action | None |
| Special | Not a starting role, but a **state** applied by Cupid |
| Effect | If one dies, the other immediately dies of heartbreak as well |
| Victory Condition | Lovers can win together regardless of their original camps |

Source: `roles/neutral.py` - `Lover`

### White Lover Wolf (Dynamic State)

| Attribute | Value |
|-----------|-------|
| Camp | Neutral |
| Night Action | None |
| Trigger Condition | Triggered when a werewolf and a villager become lovers |
| Victory Condition | Must eliminate all other players; wins when only the two lovers remain alive |

Source: `roles/neutral.py` - `WhiteLoverWolf`

---

## 11. Victory Conditions

Victory conditions are checked in the following **strict priority order**. The game ends as soon as the first satisfied condition is found.

### Priority 1: Lovers Victory

- **Condition**: exactly 2 players remain alive, and both are lovers.
- **Winners**: those two lovers.

### Priority 2: Werewolf Victory

- **Condition**: the number of living werewolves is greater than or equal to the number of living villagers, and the number of werewolves is greater than 0.
- **Exception**: an untransformed Blood Moon Apostle **does not count** toward the werewolf total.
- **Winners**: all surviving Werewolf Camp players, including untransformed Blood Moon Apostles.

### Priority 3: Villager Victory

- **Condition**: all werewolves have been eliminated (`living_werewolves = 0`).
- **Exception**: a Blood Moon Apostle counts as a **werewolf** whether transformed or not, and must also be eliminated.
- **Winners**: all surviving Villager Camp players.

Source: `victory.py` - `VictoryChecker`

---

## 12. Death Resolution

### Werewolf Kill Resolution

After the werewolves choose a target, the following checks occur in order:

1. **Witch antidote**: if `witch_saved_target == target` -> the target **survives**
2. **Guard protection**: if `guard_protected == target` -> the target **survives**
3. **Elder extra life**: if the target is the Elder and `lives > 1` -> the target **loses one life but survives**
4. **Otherwise**: the target **dies**

> Note: Guard protection and the Witch antidote are checked independently in an `if/elif` structure. There is **no** rule where "double protection causes death." If both apply to the same target, the Witch antidote is checked first and the target still survives.

Source: `engine/death_handler.py` - `_handle_werewolf_kill()`

### Witch Poison Resolution

- The poisoned target dies immediately (**ignores all protection**).
- The cause of death is recorded as `"witch_poison"`.
- This can trigger the lovers' suicide chain if applicable.

Source: `engine/death_handler.py` - `_resolve_witch_poison_death()`

### Death-Triggered Abilities

When a player with a death-triggered ability (Hunter or Alpha Wolf) dies:

1. Check the cause of death. If it is `"witch_poison"`, the ability is **disabled** and the player cannot shoot.
2. Otherwise, the player may **choose one living player to shoot**.
3. The shot target dies immediately.
4. If the shot target is a lover, that lover's partner also dies of heartbreak.

Source: `engine/death_handler.py` - `_handle_death_abilities()`, `_process_hunter_or_alpha_death()`

### Wolf Beauty Charm Chain

- When Wolf Beauty dies, the charmed target also dies if still alive.
- This triggers whether Wolf Beauty dies at night or during the day.

Source: `engine/death_handler.py` - `_handle_wolf_beauty_charm_death()`, `_resolve_wolf_beauty_charm_deaths()`

### Lovers' Suicide Chain

- When one lover dies, the other immediately dies of heartbreak.
- This can trigger during both night and day death resolution.

Source: `engine/death_handler.py` - `_handle_lover_death()`

---

## 13. Special Mechanics

### Guard + Witch Antidote Interaction

- They are resolved independently, and either one can stop a werewolf kill.
- In the current implementation, there is **no** mutually exclusive rule where double protection causes death.

### Ability Disable Mechanic

- `role.disabled = True` prevents a role from acting at night.
- It is triggered by the **Elder penalty** (Elder exiled by vote -> all Villager Camp abilities are disabled).
- It is checked in `Role.can_act_tonight()`.

Source: `roles/base.py` - `can_act_tonight()`

### Ability Usage Limits

- Roles with `max_uses` can only use their abilities a limited number of times.
- Usage is tracked by the `role.ability_uses` counter.
- This is checked in `Role.can_act_tonight()`.

### Discussion History

- **Public discussion history**: accumulates across rounds and is visible to all players during the day and voting phases.
- **Internal werewolf discussion history**: accumulates across rounds and is visible only to werewolves during night discussion.

Source: `engine/base.py`, `engine/day_phase.py`, `engine/night_phase.py`

### Action History

- Each player's agent maintains a personal **action history** of that player's own actions and statements.
- This history is provided as context for later decisions.
- It includes only the player's own actions and excludes other players' sensitive information.

Source: `engine/day_phase.py`, `engine/voting_phase.py`, `engine/night_phase.py`

---

## 14. Preset Role Compositions

When using automatic setup by player count:

### Werewolf Roles

| Player Count | Werewolf Roles |
|--------------|----------------|
| 6–8 | Werewolf x2 |
| 9–11 | Werewolf x2, Alpha Wolf |
| 12–14 | Werewolf x2, Alpha Wolf, White Wolf |
| 15–20 | Werewolf x2, Alpha Wolf, White Wolf, Wolf Beauty |

### Special Villager Roles

| Player Count | Added Roles |
|--------------|-------------|
| 6+ (always included) | Seer, Witch |
| 7+ | Guard |
| 9+ | Hunter |
| 11+ | Cupid |
| 13+ | Idiot |
| 15+ | Elder |
| 17+ | Knight |
| 19+ | Raven |

All remaining slots are filled with **Villagers** (no special abilities).

Source: `config/presets.py`

---

## 15. Timeout Settings

| Player Count | Night Timeout | Day Timeout | Vote Timeout |
|--------------|---------------|-------------|--------------|
| 6–8 | 45s | 180s | 45s |
| 9–12 | 60s | 300s | 60s |
| 13–20 | 90s | 400s | 90s |

Source: `config/presets.py` - `_get_timeouts()`

---

## Appendix: Role Summary Table

| Role Name | Camp | Implementation Status |
|-----------|------|-----------------------|
| Werewolf | Werewolf | ✅ Implemented |
| AlphaWolf | Werewolf | ✅ Implemented |
| WhiteWolf | Werewolf | ✅ Implemented |
| WolfBeauty | Werewolf | ✅ Implemented |
| GuardianWolf | Werewolf | ✅ Implemented |
| HiddenWolf | Werewolf | ✅ Implemented |
| BloodMoonApostle | Werewolf | ✅ Implemented |
| NightmareWolf | Werewolf | ✅ Implemented |
| Villager | Villager | ✅ Implemented |
| Seer | Villager | ✅ Implemented |
| Witch | Villager | ✅ Implemented |
| Hunter | Villager | ✅ Implemented |
| Guard | Villager | ✅ Implemented |
| Idiot | Villager | ✅ Implemented |
| Elder | Villager | ✅ Implemented |
| Knight | Villager | ✅ Implemented |
| Magician | Villager | ⚠️ Placeholder (not implemented) |
| Cupid | Villager | ✅ Implemented |
| Raven | Villager | ✅ Implemented |
| GraveyardKeeper | Villager | ✅ Implemented |
| Thief | Neutral | ⚠️ Placeholder (not implemented) |
| Lover | Neutral | ✅ Implemented (dynamic state) |
| WhiteLoverWolf | Neutral | ✅ Implemented (dynamic state) |

Source: `role_registry.py` - `get_role_map()`
