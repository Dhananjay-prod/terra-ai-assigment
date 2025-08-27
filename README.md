# RPG NPC Interaction System

An AI-powered NPC (Non-Player Character) system that creates dynamic, mood-aware interactions for medieval fantasy RPG games. NPCs remember past conversations and adapt their responses based on how players treat them.

## Features

- **Dynamic Mood System**: NPCs develop feelings toward individual players based on their behavior
- **Conversation Memory**: Each NPC remembers the last 3 interactions with each player
- **Contextual Responses**: AI generates appropriate medieval fantasy responses
- **Persistent Logging**: All interactions are logged with timestamps and mood states
- **Async Processing**: Efficient handling of multiple player interactions

## Prerequisites

- Python 3.7+
- Google AI API key (for Gemini model access)
- Input data file: `players.json`

## Installation

1. **Clone or download the code**
2. **Install required libraries**:
   ```bash
   pip install google-generativeai
   ```

3. **Set up your Google AI API key**:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Replace `"api key"` in the code with your actual API key

4. **Prepare your input data**:
   Create a `players.json` file with the following format:
   ```json
   [
     {
       "player_id": "player_001",
       "text": "Hello, good merchant!",
       "timestamp": "2024-01-15T10:30:00"
     },
     {
       "player_id": "player_002", 
       "text": "You're overcharging me!",
       "timestamp": "2024-01-15T10:31:00"
     }
   ]
   ```

## Quick Start

1. **Prepare your data**: Ensure `players.json` exists with player messages
2. **Run the system**:
   ```bash
   python npc_system.py
   ```
3. **Check results**: View generated interactions in `npc_interactions.jsonl`

## System Workflow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Player   │───▶│   Sort Messages  │───▶│  Initialize NPC │
│   Messages      │    │   by Timestamp   │    │  State Tracker  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Process Each Message                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Update Player  │───▶│   Build Context  │───▶│   AI Generate   │
│  Message History│    │  (Last 3 msgs +  │    │   Response +    │
│   (Keep Last 3) │    │   Current Mood)  │    │   Mood Update   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Log Complete  │◀───│  Update NPC Mood │◀───│  Parse AI JSON  │
│   Interaction   │    │  Toward Player   │    │    Response     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## How It Works

### 1. **Message Processing**
- Loads and sorts player messages chronologically
- Maintains separate conversation states for each player
- Keeps rolling history of last 3 messages per player

### 2. **Mood Evolution**
NPCs develop attitudes based on player behavior:
- **Rude/Insulting** → `angry`, `stern`  
- **Polite/Grateful** → `friendly`, `helpful`
- **Apologetic** → `neutral`, `forgiving`
- **Confused** → `patient`, `helpful`

### 3. **AI Response Generation**
Single API call generates both:
- Contextually appropriate NPC response (1 sentence)
- Updated mood state toward the specific player

### 4. **Persistent State**
Each interaction is logged with:
- Player message and NPC response
- Mood state and conversation history
- Timestamp for chronological tracking

## Output Format

The system generates `npc_interactions.jsonl` with entries like:
```json
{
  "player_id": "player_001",
  "message_text": "Thank you for your help!",
  "npc_reply": "You are most welcome, kind traveler!",
  "state_used": ["Hello there", "Can you help me?", "Thank you for your help!"],
  "npc_mood": "friendly",
  "timestamp": "2024-01-15T10:32:00"
}
```

## Customization

### Modify NPC Character Types
Edit the prompt to specify different NPC roles:
```python
# In the prompt, change this line:
"Stay in medieval NPC character (merchant, guard, elder, etc.)"
# To specific roles like:
"You are a gruff tavern keeper" or "You are a wise village elder"
```

### Adjust Mood Categories
Modify the mood options in the prompt:
```python
"NPC mood options: friendly, angry, neutral, helpful, patient, stern, dismissive"
```

### Change Memory Length
Adjust how many previous messages to remember:
```python
player_data["messages"] = player_data["messages"][-3:]  # Change -3 to desired length
```

## Rate Limiting

The system includes a 0.5-second delay between API calls to respect rate limits. Adjust if needed:
```python
await asyncio.sleep(0.5)  # Modify delay as needed
```

## Troubleshooting

**API Key Issues**: Ensure your Google AI API key is valid and has quota remaining

**JSON Parsing Errors**: The system includes fallback responses if AI output isn't valid JSON

**File Not Found**: Ensure `players.json` exists in the same directory as the script

**Rate Limiting**: If you hit API limits, increase the sleep delay in the `detect_mood_and_generate_response` function

## License

This project is open source. Feel free to modify and distribute according to your needs.
