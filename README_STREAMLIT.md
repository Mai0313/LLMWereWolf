# LLM Werewolf Streamlit UI

A simple, functional web interface for the LLM Werewolf game built with Streamlit.

## Features

- **🎮 Complete Game Control**: Start, pause, resume, and reset games
- **👁️ God Mode**: Toggle to see all player identities (admin feature)
- **📝 Real-time Events**: Watch game events unfold in real-time
- **💾 Game Logging**: Save complete game sessions to JSON files
- **📊 Game Statistics**: Track player counts, rounds, and game progress
- **🎨 Clean Interface**: Simple, distraction-free design focusing on functionality

## Quick Start

### 1. Install Dependencies

```bash
# Install Streamlit dependencies
pip install -r requirements-streamlit.txt

# Or using uv (recommended)
uv pip install -r requirements-streamlit.txt
```

### 2. Set Up Environment

Create a `.env` file with your API keys (if using LLM models):

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
XAI_API_KEY=xai-...
```

### 3. Run the UI

```bash
# Using streamlit command
streamlit run streamlit_app.py

# Or using uv
uv run streamlit run streamlit_app.py
```

The UI will open in your browser at `http://localhost:8501`

## Usage

### Starting a Game

1. **Select Configuration**: Choose from available YAML configs in the `configs/` directory
   - `demo.yaml` - Demo agents (no API key needed)
   - `gpt-5-chaos.yaml` - LLM agents (requires API keys)
   - Custom configurations you create

2. **Start Game**: Click the "Start New Game" button in the sidebar

3. **Watch the Game**: The game will run automatically with:
   - Unlimited discussion time (as requested)
   - Real-time event feed
   - Player status updates

### God Mode

Toggle the **"God Mode"** switch in the sidebar to:
- **ON**: See all player roles and identities
- **OFF**: View as a regular spectator (roles hidden until game ends)

### Game Controls

- **⏸️ Pause**: Pause the game at any time
- **▶️ Resume**: Resume a paused game
- **🔄 Reset**: End current game and start fresh

### Saving Game Logs

Click **"💾 Save Game Log"** to save the complete game session to:
- Format: `game_logs/werewolf_game_YYYYMMDD_HHMMSS.json`
- Includes: All events, timestamps, player actions, and game configuration
- Perfect for analysis, debugging, or replaying games

## Interface Overview

### Main Game Area

1. **Phase Indicator**: Shows current phase (Night/Day) with visual styling
2. **Player Grid**: Visual cards showing:
   - Player status (alive/dead)
   - Role name (hidden without God Mode)
   - AI model used
   - Status effects (protected, poisoned, charmed)
3. **Event Feed**: Real-time game events with color coding:
   - 💀 Deaths and kills (red)
   - 🗳️ Voting events (blue)
   - 💬 Discussion messages (green)
   - 🎮 Game events (purple)

### Sidebar Controls

1. **Configuration Selection**: Choose game setup
2. **God Mode Toggle**: Show/hide player roles
3. **Game Controls**: Start, pause, resume, reset
4. **Game Status**: Current round, phase, player counts
5. **Log Saving**: Export game sessions

### Statistics Panel

- **Faction Counts**: Werewolves vs Villagers (God Mode only)
- **Game Progress**: Round number, total events
- **Player Status**: Alive/dead counts

## Configuration Files

The UI works with existing YAML configuration files:

```yaml
# demo.yaml example
language: "en-US"
players:
  - name: "Alice"
    model: "demo"
  - name: "Bob"
    model: "demo"
  - name: "Carol"
    model: "demo"
```

For LLM models:

```yaml
# gpt-5-chaos.yaml example
language: "en-US"
players:
  - name: "AI_Player_1"
    model: "gpt-4"
    base_url: "https://api.openai.com/v1"
    api_key_env: "OPENAI_API_KEY"
```

## Game Modes Supported

- **Demo Mode**: Use `demo.yaml` for testing with pre-programmed responses
- **LLM Mode**: Use configurations with actual LLM models (requires API keys)
- **Mixed Mode**: Combine demo agents and LLM agents in the same game

## Technical Details

### Architecture

The Streamlit UI integrates with the existing backend through:

- **GameEngine**: Core game orchestrator
- **Event System**: Real-time event callbacks for UI updates
- **GameState**: Access to current game state and player information
- **Threading**: Non-blocking game execution using background threads

### Session Management

- Uses Streamlit's `st.session_state` for state persistence
- Game engine and events stored across reruns
- Background threads continue game execution during UI updates

### Customization

The UI is designed to be simple and functional as requested:
- No complex animations or graphics
- Focus on information display and control
- Responsive design for different screen sizes
- Color-coded events for easy scanning

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Issues**: Check `.env` file configuration
3. **Configuration Not Found**: Verify YAML files exist in `configs/`
4. **Game Not Starting**: Check console output for error messages

### Debug Mode

Add debugging by modifying the UI code to print more information to the console or display error states in the UI.

## Contributing

The Streamlit UI is designed to be a simple interface to the existing game engine. For major changes or enhancements:

1. Understand the backend architecture (see main README.md)
2. Follow the existing patterns in the codebase
3. Maintain simplicity and functionality focus
4. Test with different game configurations

## License

Same as the main LLM Werewolf project.