import streamlit as st
import threading
import time
from datetime import datetime
from pathlib import Path
import json
import sys
import os
from queue import Queue

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_werewolf.core import GameEngine
from llm_werewolf.core.utils import load_config
from llm_werewolf.core.agent import create_agent
from llm_werewolf.core.config import create_game_config_from_player_count
from llm_werewolf.core.role_registry import create_roles
from llm_werewolf.core.types import Event, GamePhase, EventType
from llm_werewolf.core.types.models import Event as EventModel
from llm_werewolf.core.config.player_config import PlayersConfig, PlayerConfig
from llm_werewolf.core.personality.personality import PredefinedPersonalities

# Page configuration
st.set_page_config(
    page_title="LLM ",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Define Model Presets for the Builder
MODEL_PRESETS = {
    "Demo (Random)": {
        "model": "demo",
        "base_url": None,
        "api_key_env": None
    },
    "GPT-4o": {
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY"
    },
    "GPT-4o-mini": {
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY"
    },
    "Claude 3.5 Sonnet": {
        "model": "claude-3-5-sonnet-20240620",
        "base_url": "https://api.anthropic.com/v1",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "DeepSeek Chat": {
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY"
    },
    "Human": {
        "model": "human",
        "base_url": None,
        "api_key_env": None
    }
}

class StreamlitGameUI:
    def __init__(self):
        self.setup_session_state()
        self.setup_sidebar()

    def setup_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'engine' not in st.session_state:
            st.session_state.engine = None
        if 'game_started' not in st.session_state:
            st.session_state.game_started = False
        if 'game_paused' not in st.session_state:
            st.session_state.game_paused = False
        if 'game_finished' not in st.session_state:
            st.session_state.game_finished = False
        if 'events' not in st.session_state:
            st.session_state.events = []
        if 'god_mode' not in st.session_state:
            st.session_state.god_mode = False
        if 'current_config' not in st.session_state:
            st.session_state.current_config = None
        if 'game_thread' not in st.session_state:
            st.session_state.game_thread = None
        if 'event_queue' not in st.session_state:
            st.session_state.event_queue = Queue()
        
        # New: Custom Builder State
        if 'custom_players' not in st.session_state:
            st.session_state.custom_players = []
        if 'builder_mode' not in st.session_state:
            st.session_state.builder_mode = False

    def setup_sidebar(self):
        """Setup sidebar controls"""
        st.sidebar.title("🐺 Werewolf Control Panel")

        # Mode Selection
        mode = st.sidebar.radio("Game Setup Mode", ["📂 Load Config File", "🛠️ Custom Builder"])
        st.session_state.builder_mode = (mode == "🛠️ Custom Builder")

        st.sidebar.markdown("---")

        if not st.session_state.builder_mode:
            # Standard Config File Loader
            config_files = list(Path("configs").glob("*.yaml"))
            if config_files:
                config_names = [f.stem for f in config_files]
                selected_config = st.sidebar.selectbox(
                    "Select Configuration",
                    config_names,
                    index=config_names.index("demo") if "demo" in config_names else 0
                )
                st.session_state.selected_config_path = f"configs/{selected_config}.yaml"
            else:
                st.sidebar.error("No configuration files found in 'configs/' directory")
        else:
            # Custom Builder UI
            self.render_custom_builder()

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

        # Save logs
        if st.session_state.events:
            if st.sidebar.button("💾 Save Game Log"):
                self.save_game_log()

        # Game info
        if st.session_state.engine:
            self.show_game_info()

    def render_custom_builder(self):
        """Render the custom player builder in sidebar"""
        st.sidebar.subheader("Add Player to Pool")
        
        with st.sidebar.form("add_player_form"):
            new_name = st.text_input("Name", value=f"Player{len(st.session_state.custom_players)+1}")
            
            # Model Selection
            model_display_name = st.selectbox("Model", list(MODEL_PRESETS.keys()))
            
            # Personality Selection
            available_personalities = ["None (Classic)"] + PredefinedPersonalities.list_available_personalities()
            selected_personality = st.selectbox("Personality", available_personalities)
            
            enable_personality = selected_personality != "None (Classic)"
            
            if st.form_submit_button("➕ Add Player"):
                model_config = MODEL_PRESETS[model_display_name]
                
                new_player_config = PlayerConfig(
                    name=new_name,
                    model=model_config["model"],
                    base_url=model_config["base_url"],
                    api_key_env=model_config["api_key_env"],
                    personality_profile=selected_personality if enable_personality else None,
                    enable_personality_system=enable_personality
                )
                
                st.session_state.custom_players.append(new_player_config)
                st.success(f"Added {new_name}")

        # Display current pool
        st.sidebar.markdown(f"**Current Pool: {len(st.session_state.custom_players)} Players**")
        
        if len(st.session_state.custom_players) > 0:
            if st.sidebar.button("🗑️ Clear All Players"):
                st.session_state.custom_players = []
                st.rerun()
            
            # Show list preview
            for i, p in enumerate(st.session_state.custom_players):
                p_info = f"{i+1}. **{p.name}** ({p.model})"
                if p.enable_personality_system:
                    p_info += f"\n   🎭 {p.personality_profile}"
                st.sidebar.markdown(p_info)
        
        if len(st.session_state.custom_players) < 6:
            st.sidebar.warning("⚠️ Need at least 6 players to start")

    def start_new_game(self):
        """Initialize and start a new game"""
        try:
            config = None
            
            # 1. Determine Config Source
            if st.session_state.builder_mode:
                # Build config from custom players
                if len(st.session_state.custom_players) < 6:
                    st.error("Need at least 6 players to start a game!")
                    return
                
                config = PlayersConfig(
                    language="zh-TW", # Default to TW for custom games
                    players=st.session_state.custom_players
                )
            else:
                # Load from file
                config = load_config(st.session_state.selected_config_path)

            # 2. Create Agents & Roles
            agents = [create_agent(p, language=config.language) for p in config.players]
            game_config = create_game_config_from_player_count(len(agents))
            roles = create_roles(role_names=game_config.role_names)

            # 3. Handle Personality System
            # Check if any player has personality enabled
            enable_personality_system = any(
                getattr(p, 'enable_personality_system', False) for p in config.players
            )

            # 4. Create Engine
            # Pass personality flag to engine
            engine = GameEngine(
                game_config, 
                language=config.language,
                enable_personality_system=enable_personality_system
            )

            # 5. Adapt Agents for Personality (If enabled)
            final_players = []
            if enable_personality_system:
                from llm_werewolf.core.personality_integration_manager import PersonalityManager
                personality_adapter = PersonalityManager.get_personality_adapter()
                
                for i, (agent, player_cfg) in enumerate(zip(agents, config.players)):
                    if getattr(player_cfg, 'enable_personality_system', False) and personality_adapter:
                        # Wrap agent with personality
                        enhanced_agent = personality_adapter.create_enhanced_agent(
                            player_id=i+1, # Temporary ID
                            base_agent=agent,
                            personality_profile_name=player_cfg.personality_profile
                        )
                        final_players.append(enhanced_agent)
                    else:
                        final_players.append(agent)
            else:
                final_players = agents

            engine.setup_game(players=final_players, roles=roles)

            # 6. Event Handling
            event_queue = st.session_state.event_queue
            
            # Clear old queue
            while not event_queue.empty():
                try: event_queue.get_nowait()
                except: break

            def event_handler(event: Event):
                event_queue.put({
                    'timestamp': datetime.now(),
                    'event': event
                })

            engine.on_event = event_handler

            # 7. Update Session State
            st.session_state.engine = engine
            st.session_state.game_started = True
            st.session_state.game_paused = False
            st.session_state.game_finished = False
            st.session_state.events = []
            st.session_state.current_config = config

            # 8. Start Background Thread
            self.run_game_async()
            st.rerun()

        except Exception as e:
            import traceback
            error_msg = f"Failed to start game: {str(e)}"
            st.error(error_msg)
            st.code(traceback.format_exc())

    def run_game_async(self):
        """Run the game in a background thread"""
        def game_worker(engine, event_queue):
            try:
                if engine:
                    result = engine.play_game()
                    event_queue.put({'type': 'game_finished'})
            except Exception as e:
                error_event = EventModel(
                    event_type=EventType.ERROR,
                    message=f'Game error: {str(e)}',
                    round_number=0,
                    phase="ERROR",
                    data={'error': str(e)}
                )
                event_queue.put({
                    'timestamp': datetime.now(),
                    'event': error_event
                })
                event_queue.put({'type': 'game_finished'})
                import traceback
                print(f"Background thread error: {e}")
                print(traceback.format_exc())

        engine = st.session_state.engine
        event_queue = st.session_state.event_queue

        st.session_state.game_thread = threading.Thread(
            target=game_worker,
            args=(engine, event_queue),
            daemon=True
        )
        st.session_state.game_thread.start()

    def pause_game(self):
        st.session_state.game_paused = True
        st.sidebar.success("Game paused")

    def resume_game(self):
        st.session_state.game_paused = False
        st.sidebar.success("Game resumed")

    def reset_game(self):
        st.session_state.engine = None
        st.session_state.game_started = False
        st.session_state.game_paused = False
        st.session_state.game_finished = False
        st.session_state.events = []
        st.rerun()

    def process_event_queue(self):
        if 'event_queue' not in st.session_state: return

        event_queue = st.session_state.event_queue
        while not event_queue.empty():
            try:
                event_data = event_queue.get_nowait()
                if isinstance(event_data, dict) and 'type' in event_data:
                    if event_data['type'] == 'game_finished':
                        st.session_state.game_finished = True
                    continue
                if 'event' in event_data and 'timestamp' in event_data:
                    st.session_state.events.append(event_data)
            except Exception:
                break

    def save_game_log(self):
        if not st.session_state.events:
            st.sidebar.warning("No events to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"game_logs/werewolf_game_{timestamp}.json"
        Path("game_logs").mkdir(exist_ok=True)

        log_data = {
            'timestamp': timestamp,
            'events': [
                {
                    'timestamp': event['timestamp'].isoformat(),
                    'type': str(event['event'].event_type),
                    'message': event['event'].message,
                    'round': event['event'].round_number,
                    'phase': str(event['event'].phase),
                    'data': getattr(event['event'], 'data', None)
                }
                for event in st.session_state.events
            ]
        }
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            st.sidebar.success(f"Log saved: {log_file}")
        except Exception as e:
            st.sidebar.error(f"Save failed: {str(e)}")

    def show_game_info(self):
        engine = st.session_state.engine
        game_state = engine.get_game_state() if engine else None

        if game_state:
            st.sidebar.markdown("### Game Status")
            st.sidebar.write(f"**Round:** {game_state.round_number}")
            st.sidebar.write(f"**Phase:** {game_state.get_phase().value}")
            alive_count = len([p for p in game_state.players if p.is_alive()])
            st.sidebar.write(f"**Alive:** {alive_count}/{len(game_state.players)}")

            if st.session_state.god_mode:
                st.sidebar.markdown("### Roles (God Mode)")
                for player in game_state.players:
                    icon = "🟢" if player.is_alive() else "💀"
                    # Add personality icon if enabled
                    p_icon = "🎭" if player.has_personality_system() else ""
                    st.sidebar.write(f"{icon} {player.name} {p_icon}: {player.get_role_name()}")

    def render_main_content(self):
        st.markdown('<div class="game-header"><h1>LLM </h1></div>', unsafe_allow_html=True)

        if not st.session_state.engine:
            st.info("👈 Use sidebar to configure and start the game")
            return

        engine = st.session_state.engine
        game_state = engine.get_game_state()

        if not game_state:
            st.info("Initializing...")
            return

        phase = game_state.get_phase()
        if phase == GamePhase.NIGHT:
            st.markdown(f'<div class="phase-night">🌙 Night Phase - Round {game_state.round_number}</div>', unsafe_allow_html=True)
        elif phase in [GamePhase.DAY_DISCUSSION, GamePhase.DAY_VOTING]:
            st.markdown(f'<div class="phase-day">☀️ Day Phase - Round {game_state.round_number}</div>', unsafe_allow_html=True)
        elif phase == GamePhase.ENDED:
            st.markdown('<div class="phase-day">🏁 Game Ended</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            self.render_players_section(game_state)
            self.render_events_section()
        with col2:
            self.render_game_statistics(game_state)

    def render_players_section(self, game_state):
        st.subheader("👥 Players")
        cols = st.columns(4)
        for i, player in enumerate(game_state.players):
            with cols[i % 4]:
                status_class = "player-alive" if player.is_alive() else "player-dead"
                status_icon = "🟢" if player.is_alive() else "💀"
                role_display = player.get_role_name() if st.session_state.god_mode or not player.is_alive() else "???"
                
                # Show personality info
                personality_info = ""
                if hasattr(player, 'personality_profile') and player.personality_profile:
                     personality_info = f"<br>🎭 {player.personality_profile}"

                st.markdown(f"""
                <div class="player-card {status_class}">
                    <strong>{status_icon} {player.name}</strong><br>
                    <small>Role: {role_display}<br>
                    Model: {player.ai_model}
                    {personality_info}</small>
                </div>
                """, unsafe_allow_html=True)

    def render_events_section(self):
        st.subheader("📜 Game Events")
        if not st.session_state.events:
            st.info("Waiting for events...")
            return
        
        # Reverse to show newest on top usually, but chat style is bottom-up
        # Here we show last 20 events
        for event_data in st.session_state.events[-20:]:
            event = event_data['event']
            timestamp = event_data['timestamp'].strftime("%H:%M:%S")
            
            icon = "📝"
            color = "#6c757d"
            msg_lower = event.message.lower()
            
            if "died" in msg_lower or "killed" in msg_lower:
                icon = "💀"; color = "#dc3545"
            elif "vote" in msg_lower:
                icon = "🗳️"; color = "#007bff"
            elif ":" in event.message: # Likely speech
                icon = "💬"; color = "#28a745"
            elif "game" in msg_lower:
                icon = "🎮"; color = "#6f42c1"
                
            st.markdown(f"""
            <div class="event-message" style="border-left-color: {color};">
                <small>{icon} [{timestamp}]</small><br>
                {event.message}
            </div>
            """, unsafe_allow_html=True)

    def render_game_statistics(self, game_state):
        st.subheader("📊 Stats")
        alive_count = len([p for p in game_state.players if p.is_alive()])
        st.write(f"**Alive:** {alive_count}")
        st.write(f"**Dead:** {len(game_state.players) - alive_count}")
        
        if st.session_state.god_mode:
            # Show faction counts if in god mode
            wolf_count = len([p for p in game_state.players if "wolf" in p.get_role_name().lower() and p.is_alive()])
            st.write(f"**🐺 Wolves Alive:** {wolf_count}")

    def run(self):
        self.process_event_queue()
        self.render_main_content()
        if st.session_state.game_started and not st.session_state.game_finished:
            time.sleep(2)
            st.rerun()

def main():
    if 'event_queue' not in st.session_state:
        st.session_state.event_queue = Queue()
    ui = StreamlitGameUI()
    ui.run()

if __name__ == "__main__":
    main()