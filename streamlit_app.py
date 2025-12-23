import streamlit as st
import threading
import time
from datetime import datetime
from pathlib import Path
import json
import asyncio
from typing import Dict, List, Optional

from llm_werewolf.core import GameEngine
from llm_werewolf.core.utils import load_config
from llm_werewolf.core.agent import create_agent
from llm_werewolf.core.config import create_game_config_from_player_count
from llm_werewolf.core.role_registry import create_roles
from llm_werewolf.core.types import Event, GamePhase
from llm_werewolf.core.serialization import save_game_state

# Page configuration
st.set_page_config(
    page_title="LLM Werewolf Game",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.game-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 1rem;
}
.player-card {
    padding: 0.5rem;
    margin: 0.25rem;
    border-radius: 8px;
    border: 1px solid #ddd;
}
.player-alive {
    background-color: #d4edda;
    border-color: #c3e6cb;
}
.player-dead {
    background-color: #f8d7da;
    border-color: #f5c6cb;
}
.event-message {
    padding: 0.5rem;
    margin: 0.25rem 0;
    border-radius: 5px;
    border-left: 4px solid #007bff;
}
.phase-night {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
    border-radius: 8px;
}
.phase-day {
    background-color: #f39c12;
    color: white;
    padding: 1rem;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

class StreamlitGameUI:
    def __init__(self):
        self.setup_session_state()
        self.setup_sidebar()

    def setup_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'engine' not in st.session_state:
            st.session_state.engine = None
            st.session_state.game_started = False
            st.session_state.game_paused = False
            st.session_state.game_finished = False
            st.session_state.events = []
            st.session_state.god_mode = False
            st.session_state.current_config = None
            st.session_state.game_thread = None

    def setup_sidebar(self):
        """Setup sidebar controls"""
        st.sidebar.title("🐺 Werewolf Control Panel")

        # Configuration selection
        config_files = list(Path("configs").glob("*.yaml"))
        if config_files:
            config_names = [f.stem for f in config_files]
            selected_config = st.sidebar.selectbox(
                "Select Configuration",
                config_names,
                index=config_names.index("demo") if "demo" in config_names else 0
            )
            st.session_state.selected_config = f"configs/{selected_config}.yaml"
        else:
            st.sidebar.error("No configuration files found in 'configs/' directory")
            return

        st.sidebar.markdown("---")

        # God mode toggle
        st.session_state.god_mode = st.sidebar.toggle(
            "👁️ God Mode",
            value=st.session_state.god_mode,
            help="When enabled, you can see all player roles"
        )

        # Game controls
        st.sidebar.markdown("### Game Controls")

        if not st.session_state.game_started:
            if st.sidebar.button("🚀 Start New Game", type="primary"):
                self.start_new_game()
        else:
            col1, col2 = st.sidebar.columns(2)

            with col1:
                if not st.session_state.game_paused and not st.session_state.game_finished:
                    if st.button("⏸️ Pause"):
                        self.pause_game()
                elif st.session_state.game_paused:
                    if st.button("▶️ Resume"):
                        self.resume_game()

            with col2:
                if st.sidebar.button("🔄 Reset"):
                    self.reset_game()

        st.sidebar.markdown("---")

        # Save logs
        if st.session_state.events:
            if st.sidebar.button("💾 Save Game Log"):
                self.save_game_log()

        # Game info
        if st.session_state.engine:
            self.show_game_info()

    def start_new_game(self):
        """Initialize and start a new game"""
        try:
            # Load configuration
            config = load_config(st.session_state.selected_config)
            agents = [create_agent(p, language=config.language) for p in config.players]
            game_config = create_game_config_from_player_count(len(agents))
            roles = create_roles(role_names=game_config.role_names)

            # Create engine
            engine = GameEngine(game_config, language=config.language)
            engine.setup_game(players=agents, roles=roles)

            # Set up event handler
            def event_handler(event: Event):
                st.session_state.events.append({
                    'timestamp': datetime.now(),
                    'event': event
                })

            engine.on_event = event_handler

            # Store in session state
            st.session_state.engine = engine
            st.session_state.game_started = True
            st.session_state.game_paused = False
            st.session_state.game_finished = False
            st.session_state.events = []
            st.session_state.current_config = config

            # Start game in background thread
            self.run_game_async()

            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Failed to start game: {str(e)}")

    def run_game_async(self):
        """Run the game in a background thread"""
        def game_worker():
            try:
                engine = st.session_state.engine
                if engine:
                    result = engine.play_game()
                    st.session_state.game_finished = True
            except Exception as e:
                st.session_state.events.append({
                    'timestamp': datetime.now(),
                    'event': type('Event', (), {
                        'event_type': 'ERROR',
                        'message': f'Game error: {str(e)}',
                        'round_number': 0,
                        'phase': None
                    })()
                })
                st.session_state.game_finished = True

        st.session_state.game_thread = threading.Thread(target=game_worker, daemon=True)
        st.session_state.game_thread.start()

    def pause_game(self):
        """Pause the game"""
        st.session_state.game_paused = True
        st.sidebar.success("Game paused")

    def resume_game(self):
        """Resume the game"""
        st.session_state.game_paused = False
        st.sidebar.success("Game resumed")

    def reset_game(self):
        """Reset the game"""
        st.session_state.engine = None
        st.session_state.game_started = False
        st.session_state.game_paused = False
        st.session_state.game_finished = False
        st.session_state.events = []
        st.rerun()

    def save_game_log(self):
        """Save game events to a log file"""
        if not st.session_state.events:
            st.sidebar.warning("No events to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"game_logs/werewolf_game_{timestamp}.json"

        Path("game_logs").mkdir(exist_ok=True)

        log_data = {
            'timestamp': timestamp,
            'config': st.session_state.selected_config,
            'events': [
                {
                    'timestamp': event['timestamp'].isoformat(),
                    'type': event['event'].event_type.value if hasattr(event['event'].event_type, 'value') else str(event['event'].event_type),
                    'message': event['event'].message,
                    'round': event['event'].round_number,
                    'phase': event['event'].phase.value if hasattr(event['event'].phase, 'value') else str(event['event'].phase),
                    'data': event['event'].data if hasattr(event['event'], 'data') else None
                }
                for event in st.session_state.events
            ]
        }

        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            st.sidebar.success(f"Game log saved to {log_file}")
        except Exception as e:
            st.sidebar.error(f"Failed to save log: {str(e)}")

    def show_game_info(self):
        """Display current game information in sidebar"""
        engine = st.session_state.engine
        game_state = engine.get_game_state() if engine else None

        if game_state:
            st.sidebar.markdown("### Game Status")
            st.sidebar.write(f"**Round:** {game_state.round_number}")
            st.sidebar.write(f"**Phase:** {game_state.get_phase().value}")

            alive_count = len([p for p in game_state.players if p.is_alive()])
            st.sidebar.write(f"**Alive Players:** {alive_count}/{len(game_state.players)}")

            if st.session_state.god_mode:
                st.sidebar.markdown("### Player Roles (God Mode)")
                for player in game_state.players:
                    status_icon = "🟢" if player.is_alive() else "💀"
                    role_info = f"{player.get_role_name()}" if st.session_state.god_mode else "???"
                    st.sidebar.write(f"{status_icon} {player.name}: {role_info}")

    def render_main_content(self):
        """Render the main content area"""
        st.markdown('<div class="game-header"><h1>🐺 LLM Werewolf Game</h1></div>', unsafe_allow_html=True)

        if not st.session_state.engine:
            st.info("👈 Select a configuration and click 'Start New Game' to begin")
            return

        engine = st.session_state.engine
        game_state = engine.get_game_state()

        if not game_state:
            st.info("Game is initializing...")
            return

        # Phase indicator
        phase = game_state.get_phase()
        if phase == GamePhase.NIGHT:
            st.markdown(f'<div class="phase-night">🌙 Night Phase - Round {game_state.round_number}</div>', unsafe_allow_html=True)
        elif phase in [GamePhase.DAY_DISCUSSION, GamePhase.DAY_VOTING]:
            st.markdown(f'<div class="phase-day">☀️ Day Phase - Round {game_state.round_number}</div>', unsafe_allow_html=True)
        elif phase == GamePhase.ENDED:
            st.markdown('<div class="phase-day">🏁 Game Ended</div>', unsafe_allow_html=True)

        # Create columns for layout
        col1, col2 = st.columns([2, 1])

        with col1:
            self.render_players_section(game_state)
            self.render_events_section()

        with col2:
            self.render_game_statistics(game_state)

    def render_players_section(self, game_state):
        """Render players grid"""
        st.subheader("👥 Players")

        # Create grid of players
        cols = st.columns(min(4, len(game_state.players)))

        for i, player in enumerate(game_state.players):
            with cols[i % 4]:
                status_class = "player-alive" if player.is_alive() else "player-dead"
                status_icon = "🟢" if player.is_alive() else "💀"

                # Player role (hidden unless god mode)
                role_display = player.get_role_name() if st.session_state.god_mode or not player.is_alive() else "???"

                # Status effects
                status_effects = []
                if hasattr(player, 'statuses'):
                    if 'protected' in player.statuses:
                        status_effects.append("🛡️")
                    if 'poisoned' in player.statuses:
                        status_effects.append("☠️")
                    if 'charmed' in player.statuses:
                        status_effects.append("💕")

                status_text = " ".join(status_effects)

                st.markdown(f"""
                <div class="player-card {status_class}">
                    <strong>{status_icon} {player.name}</strong><br>
                    Role: {role_display}<br>
                    Model: {player.ai_model}<br>
                    {status_text}
                </div>
                """, unsafe_allow_html=True)

    def render_events_section(self):
        """Render game events feed"""
        st.subheader("📜 Game Events")

        if not st.session_state.events:
            st.info("No events yet...")
            return

        # Show recent events (last 20)
        recent_events = st.session_state.events[-20:]

        for event_data in recent_events:
            event = event_data['event']
            timestamp = event_data['timestamp'].strftime("%H:%M:%S")

            # Color code by event type
            event_type = str(event.event_type).upper() if hasattr(event.event_type, 'upper') else str(event.event_type)

            if 'DIED' in event_type or 'KILL' in event_type:
                icon = "💀"
                color = "#dc3545"
            elif 'VOTE' in event_type:
                icon = "🗳️"
                color = "#007bff"
            elif 'DISCUSSION' in event_type or 'SPEAK' in event_type:
                icon = "💬"
                color = "#28a745"
            elif 'GAME' in event_type:
                icon = "🎮"
                color = "#6f42c1"
            else:
                icon = "📝"
                color = "#6c757d"

            st.markdown(f"""
            <div class="event-message" style="border-left-color: {color};">
                <small>{icon} [{timestamp}]</small><br>
                {event.message}
            </div>
            """, unsafe_allow_html=True)

    def render_game_statistics(self, game_state):
        """Render game statistics panel"""
        st.subheader("📊 Statistics")

        # Player counts by faction
        werewolves = []
        villagers = []
        neutrals = []

        for player in game_state.players:
            if not player.is_alive():
                continue

            role_name = player.get_role_name().lower()
            if st.session_state.god_mode:
                if 'wolf' in role_name or 'werewolf' in role_name:
                    werewolves.append(player.name)
                elif any(role in role_name for role in ['seer', 'witch', 'hunter', 'guard', 'villager', 'idiot']):
                    villagers.append(player.name)
                else:
                    neutrals.append(player.name)
            else:
                # In normal mode, we can't know factions until game ends
                pass

        if st.session_state.god_mode or game_state.get_phase() == GamePhase.ENDED:
            st.write(f"**🐺 Werewolves:** {len(werewolves)}")
            if werewolves and st.session_state.god_mode:
                for wolf in werewolves:
                    st.write(f"  • {wolf}")

            st.write(f"**👥 Villagers:** {len(villagers)}")
            if villagers and st.session_state.god_mode:
                for villager in villagers:
                    st.write(f"  • {villager}")

            st.write(f"**⚖️ Neutrals:** {len(neutrals)}")
            if neutrals and st.session_state.god_mode:
                for neutral in neutrals:
                    st.write(f"  • {neutral}")
        else:
            alive_count = len([p for p in game_state.players if p.is_alive()])
            st.write(f"**🔮 Alive Players:** {alive_count}")

        # Round information
        st.markdown("---")
        st.write(f"**Current Round:** {game_state.round_number}")
        st.write(f"**Total Events:** {len(st.session_state.events)}")

        # Game progress
        if hasattr(game_state, 'day_number'):
            st.write(f"**Day Number:** {game_state.day_number}")

    def run(self):
        """Main application loop"""
        self.render_main_content()

        # Auto-refresh every 2 seconds if game is running
        if st.session_state.game_started and not st.session_state.game_finished:
            time.sleep(2)
            st.rerun()

# Main application
def main():
    ui = StreamlitGameUI()
    ui.run()

if __name__ == "__main__":
    main()