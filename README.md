# Web Agent

A Python-based web automation agent with browser control, visual capabilities, and machine learning-powered ad rating functionality.

## Features

- Browser automation using Selenium
- Click and scroll interactions
- Screenshot capture and image-based element finding
- Action recording and playback
- Visual content processing with OpenCV
- Text extraction from web pages
- Logging of all actions
- Machine learning-based ad rating prediction
- Training mode for learning from user demonstrations
- Automatic ad detection and classification

## Requirements

- Python 3.8+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

The agent can be used either as a standalone application or as an MCP server.

### MCP Server Usage

The agent is available as an MCP server, providing tools for browser automation and ad rating:

1. **Initialize with Custom Chrome Profile**:
```python
use_mcp_tool(
    server_name="ad-agent",
    tool_name="initialize_agent",
    arguments={
        "profile_path": "C:/Users/YourUser/AppData/Local/Google/Chrome/User Data"
    }
)
```

2. **Start Training Mode**:
```python
use_mcp_tool(
    server_name="ad-agent",
    tool_name="start_training",
    arguments={
        "url": "https://example.com"
    }
)
```

3. **Rate Current Sequence**:
```python
use_mcp_tool(
    server_name="ad-agent",
    tool_name="rate_sequence",
    arguments={
        "rating": 0.8
    }
)
```

4. **Get Predictions**:
```python
use_mcp_tool(
    server_name="ad-agent",
    tool_name="predict_rating",
    arguments={
        "url": "https://example.com"
    }
)
```

5. **Close Agent**:
```python
use_mcp_tool(
    server_name="ad-agent",
    tool_name="close_agent",
    arguments={}
)
```

### Standalone CLI Usage

Alternatively, use the command-line interface (main.py):

```bash
# Training Mode
python src/main.py --url "https://example.com" --mode train

# Prediction Mode
python src/main.py --url "https://example.com" --mode predict

# Additional Commands
python src/main.py --url "https://example.com" --mode predict --scroll down --scroll-amount 500
python src/main.py --url "https://example.com" --mode predict --click "100,200"
```

## Agent Capabilities

### Browser Control
- Navigate to URLs
- Click at specific coordinates
- Scroll up/down
- Capture screenshots

### Visual Processing
- Template matching for finding elements
- Image-based interaction
- Visual content analysis
- Ad content detection and classification

### Machine Learning
- Learn from user demonstrations
- Extract features from user interactions
- Predict ad ratings based on interaction patterns
- Save and load training data
- Continuous learning capabilities

### Action Recording
- Record all agent actions
- Save actions to JSON files
- Timestamp and parameter logging
- Training sequence management

### Ad Analysis
- Automatic ad detection
- Classification of ad types (image, video, iframe)
- Position tracking
- Content analysis

### Text Processing
- Extract page text
- Process text content
- Ad text analysis

## Training Process

The agent learns from your interactions through the following process:

1. **Data Collection**
   - Records your browsing patterns
   - Tracks interactions with ads
   - Captures timing and engagement metrics
   - Stores your ratings for each interaction sequence

2. **Feature Extraction**
   - Analyzes scroll patterns
   - Measures time spent on ads
   - Counts clicks and interactions
   - Processes visual content
   - Extracts text features

3. **Model Training**
   - Uses neural network to learn patterns
   - Correlates actions with ratings
   - Identifies successful interaction patterns
   - Continuously improves with more data

4. **Prediction**
   - Analyzes new ads in real-time
   - Predicts ratings based on learned patterns
   - Provides confidence scores
   - Explains rating factors

## Project Structure

```
agent-project/
├── src/
│   ├── agent.py        # Main agent implementation
│   ├── main.py         # Command-line interface
│   ├── ml_model.py     # Machine learning components
│   └── mcp_server.py   # MCP server implementation
├── logs/               # Action and error logs
├── training_data/      # Saved training sequences
├── models/             # Trained model files
├── requirements.txt    # Python dependencies
└── README.md          # Documentation
```

## Chrome Profile Configuration

The agent can use a specific Chrome profile for automation:

1. **Find Your Chrome Profile Directory**:
   - Windows: `C:\Users\YourUser\AppData\Local\Google\Chrome\User Data`
   - macOS: `~/Library/Application Support/Google/Chrome`
   - Linux: `~/.config/google-chrome`

2. **Profile Selection**:
   - Default profile: Use the base User Data directory
   - Specific profile: Add profile name (e.g., "Profile 1", "Profile 2")

3. **Usage Example**:
   ```python
   # Using default profile
   profile_path = "C:/Users/YourUser/AppData/Local/Google/Chrome/User Data"
   
   # Using specific profile
   profile_path = "C:/Users/YourUser/AppData/Local/Google/Chrome/User Data/Profile 1"
   ```

Note: Using a custom Chrome profile allows the agent to:
- Access logged-in sessions
- Use installed extensions
- Maintain cookies and site preferences
- Keep browsing history and bookmarks

## Logs and Data

- **Action Logs**: `logs/actions_[timestamp].json`
- **Training Data**: `training_data/training_data_[timestamp].json`
- **Model Files**: `models/ad_rating_model`
- **General Logs**: `logs/agent_[timestamp].log`
