import json
from datetime import datetime
from collections import defaultdict
import google.generativeai as genai
import asyncio

client = genai.configure(api_key="AIzaSyCafgtrf9ICUnxRWoc9SrKkb9YQquF7wH8")
model = genai.GenerativeModel("gemini-2.0-flash")

with open("players.json", "r") as f:
    messages = json.load(f)

messages.sort(key=lambda m: datetime.fromisoformat(m["timestamp"])) 

player_state = defaultdict(lambda: {
    "messages": [], 
    "npc_mood": "neutral", 
    "player_mood": "neutral",
    "conversation_history": [],
    "interaction_count": 0
})

async def detect_mood_and_generate_response(player_id, message, player_data):
    
    last_messages = player_data["messages"]
    current_npc_mood = player_data["npc_mood"]
    
    # Build conversation context
    conversation_context = ""
    if len(last_messages) > 1:
        conversation_context = "\nPrevious conversation:\n" + "\n".join([
            f"Player: {msg}" for msg in last_messages[:-1]
        ])
    
    prompt = f"""You are a village NPC in a medieval fantasy RPG. Do two things:

1. Respond to the player's message as the NPC
2. Determine how YOU (the NPC) feel about this player based on their behavior, their tone, and your past interactions.

Player's message: '{message}'
Your current mood toward this player: {current_npc_mood}
{conversation_context}

NPC mood options: friendly, angry, neutral, helpful, patient, stern, dismissive

Consider:
- If player is rude/insulting → you become angry/stern
- If player is polite/grateful → you become friendly/helpful  
- If player apologizes after being rude → you become more neutral/forgiving
- If player is confused → you become patient/helpful
- Your mood should evolve based on how this player treats you

Response as JSON:
{{
    "npc_response": "Your response as the NPC in 1 sentences",
    "npc_mood": "how_you_feel_about_this_player"
}}

Stay in medieval NPC character (merchant, guard, elder, etc.)"""

    try:
        await asyncio.sleep(0.5)  # Rate limiting
        response = await asyncio.to_thread(model.generate_content, prompt)
        response_text = response.text.strip()
        
        # Simple JSON parsing
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_json = json.loads(json_match.group())
            npc_response = response_json.get("npc_response", "Greetings, traveler.")
            npc_mood = response_json.get("npc_mood", current_npc_mood)
            return npc_response, npc_mood
        else:
            return "Greetings, traveler.", current_npc_mood
            
    except Exception as e:
        print(f"  AI call failed: {e}")
        return "Greetings, traveler.", current_npc_mood
    
def log_interaction(player_id, message, npc_reply, player_data, timestamp):
    """Log the interaction and write to file"""
    
    log_entry = {
        "player_id": player_id,
        "message_text": message,
        "npc_reply": npc_reply,
        "state_used": player_data["messages"].copy(),
        "npc_mood": player_data["npc_mood"],
        "timestamp": timestamp
    }
    
    with open("npc_interactions.jsonl", "a", encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + "\n")

async def main():
    # Clear log file
    with open("npc_interactions.jsonl", "w") as f:
        f.write("")
    
    # Process each message
    for i, msg in enumerate(messages):
        player_id = msg["player_id"]
        message = msg["text"]
        timestamp = msg["timestamp"]
        
        print(f"Processing {i+1}/{len(messages)}: Player {player_id}")
        
        # Get player data and update history
        player_data = player_state[player_id]
        player_data["messages"].append(message)
        player_data["messages"] = player_data["messages"][-3:]
        
        # Single AI call for response + NPC mood
        npc_reply, npc_mood = await detect_mood_and_generate_response(
            player_id, message, player_data
        )
        
        # Update NPC mood toward this player
        player_data["npc_mood"] = npc_mood
        
        # Log interaction
        log_interaction(player_id, message, npc_reply, player_data, timestamp)

if __name__ == "__main__":
    asyncio.run(main())  
