import json, os, time,requests
from collections import deque

# Dummy LLM wrapper – replace with OpenAI, Ollama, etc.
def llm_chat(prompt: str) -> str:
    '''
    Call your local LLM / API.  For demo purposes this just echoes.
    Replace with something like:
        response = openai.ChatCompletion.create(
              model="gpt-4o-mini",
              messages=[{"role":"user","content":prompt}]
          )
    '''
    system_prompt = "You are a helpful AI assistant. Be concise and friendly."
    llm_provider = "ollama"
    try:
        if llm_provider == "ollama":
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "tinyllama:latest",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"[Error: {response.status_code}]"
    except Exception as e:
        return f"[Error: {e}]"
    #return f"[LLM echo] {prompt[:75]}..."

# ------------------------------------------------------------------
class SmallAgent:
    def __init__(self, name: str, memory_size: int = 4):
        self.name = name
        self.history = deque(maxlen=memory_size)  # simple short‑term memory

    # --- perception ------------------------------------------------
    def ingest(self, new_msg: str):
        self.history.append({"role": "user", "content": new_msg})

    # --- planning --------------------------------------------------
    def plan(self) -> str:
        # Very dumb: always respond.  Plug in a policy later.
        recent = [h["content"] for h in self.history]
        prompt = "\n".join(recent)
        
        return prompt

    # --- acting ----------------------------------------------------
    def act(self):
        context = self.plan()
        reply = llm_chat(context)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    # --- expose ----------------------------------------------------
    def chat(self, user_msg: str):
        self.ingest(user_msg)
        response = self.act()
        # You can also log to a file or cloud
        print(f"{self.name} says: {response}")
        return response

# ------------------------------------------------------------------
if __name__ == "__main__":
    # Example of a 2‑agent loop – you can bring in a second one
    agentA = SmallAgent("AgentA")
    agentB = SmallAgent("AgentB")

    # Simulated conversation
    turns = [
        ("Kai", "Hello from the coding side!"),
        ("Kai", "We just built an agent from scratch in Python"),
        ("Kai", "Working on v9 with browsing and memory persistence"),
    ]

    for speaker, msg in turns:
        # Route to the next agent in the chain
        if speaker == "Kai":
            # Kai messages the first agent
           
            agentA.chat(msg)
            '''
        else:
            # AgentA replies to AgentB, then back to Kai
            reply = agentA.chat(msg)
            agentB.chat(reply)
            '''