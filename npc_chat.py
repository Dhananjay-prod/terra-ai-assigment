import json
from datetime import datetime
from collections import defaultdict
from groq import Groq
client = Groq(api_key="key")

with open("players.json", "r") as f:
    messages = json.load(f)
messages.sort(key=lambda m: datetime.fromisoformat(m["timestamp"])) 
"""
check
for x in messages[:5]:
    print(x)
"""
player_state = defaultdict(lambda: {"messages": [], "npc_mood": "neutral"})
def update_mood(message: str, current_mood: str):
    text = message.lower()
    angry_words = ["stupid", "hate", "boring", "useless","first!","it!","time","day","hogging","slow","wasting"]
    if any(word in text for word in angry_words):
        return "angry"
    friendly_words = ["help", "please", "thanks", "hello", "hi","appreciate","invaluable","safe","experience","helpful","appreciated"]
    if any(word in text for word in friendly_words):
        return "friendly"
    return current_mood

for msg in messages:
    pid = msg["player_id"]  
    text = msg["text"]

    player_state[pid]["messages"].append(text)
    player_state[pid]["messages"] = player_state[pid]["messages"][-3:] 
    player_state[pid]["npc_mood"] = update_mood(text,player_state[pid]["npc_mood"])

def generate_npc_reply(player_idx): 
    player_id= int(player_idx)
    if player_id not in player_state :
        return "And just who you might be traveller?"
    last_msgs = player_state[player_id]["messages"]
    mood = player_state[player_id]["npc_mood"]

    print(f" Player {player_id}'s last messages: {last_msgs}, mood identified as {mood}")

    joined_msgs = "\n".join([f"- {m}" for m in last_msgs])

    prompt = f""" You are a NPC in a text fantasy adventure game set in a medieval world. Your personality depends on you current npc mood.
    The player's last messages were:{joined_msgs}
    Current NPC mood: {mood}
    Respond as the NPC,staying character, in 2 or 3 sentences.
    """
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7
    )
    reply = response.choices[0].message.content.strip()
    player_state[player_id]["npc_reply"] = reply
    return reply

"""
check 
if 1 in player_state:
    print("last 3 messages:")
    for msg in player_state[1]["messages"][-3:]:
        print("**",msg)
    print(player_state[1]["npc_mood"])
else:
    print("none")

#npc_text=generate_npc_reply("24")
#print("npc:",npc_text)
"""

def log_interaction(player_id,npc_reply,timestamp,msg_id):

    last_msgs = player_state[player_id]["messages"][-3:]
    npc_mood = player_state[player_id]["npc_mood"]
    message_text=last_msgs[-1]
    log_entry = {
        "player_id": player_id,
        "message_text": message_text,
        "npc_reply": npc_reply,
        "state_used": last_msgs,
        "npc_mood": npc_mood,
        "timestamp": timestamp
    }

    print(json.dumps(log_entry,indent=5))
    if True:
        with open("logs.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n") 
x=93
msg = messages[x]
pid = int(msg["player_id"])
npc_text = generate_npc_reply(pid)
log_interaction(pid, npc_text, msg["timestamp"],msg_id=x)