"""
step4_multiagent.py - Multi-Agent Collaboration

Builds on step3_session.py
Multiple agents working together

Step 1: 4 tools
Step 2: Connect to LLM
Step 3: Session/memory
Step 4: Multi-agent collaboration
"""
import json
import requests

# Copy base from step3
def read(filepath, limit=100, offset=0):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return {"ok": True, "content": "".join(lines[offset:offset+limit]), "total_lines": len(lines)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def write(filepath, content):
    try:
        import os
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def edit(filepath, old_string, new_string):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content.replace(old_string, new_string)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def bash(command, timeout=30):
    try:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def execute_tool(tool_name, args):
    if tool_name == "read": return read(**args)
    elif tool_name == "write": return write(**args)
    elif tool_name == "edit": return edit(**args)
    elif tool_name == "bash": return bash(**args)
    else: return {"ok": False, "error": f"Unknown tool: {tool_name}"}

def call_llm(messages, model="llama3.2:3b"):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# =============================================
# Base Agent
# =============================================
class Agent:
    """Simple agent with role and chat capability"""
    
    def __init__(self, name, role, system_prompt, model="llama3.2:3b"):
        self.name = name
        self.role = role
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def chat(self, user_input):
        """Chat with this agent"""
        self.messages.append({"role": "user", "content": user_input})
        response = call_llm(self.messages, self.model)
        self.messages.append({"role": "assistant", "content": response})
        return response

# =============================================
# Multi-Agent System (Specialists)
# =============================================
class MultiAgentSystem:
    """
    Main agent + Specialist agents.
    
    Architecture:
    User -> Main (planner) -> Specialist -> Result
    """
    
    def __init__(self):
        self.main = Agent(
            name="Main",
            role="planner",
            system_prompt="You are Main, the project planner. Break down tasks and delegate."
        )
        
        self.specialists = {
            "researcher": Agent(
                name="Researcher",
                role="research",
                system_prompt="You are a research expert. Find and summarize information. Be concise."
            ),
            "coder": Agent(
                name="Coder",
                role="coding",
                system_prompt="You are a coding expert. Write clean Python code. Follow best practices."
            ),
            "writer": Agent(
                name="Writer",
                role="writing",
                system_prompt="You are a creative writer. Write engaging content. Be clear and concise."
            ),
        }
    
    def delegate(self, task):
        """Route task to appropriate specialist"""
        task_lower = task.lower()
        
        if any(w in task_lower for w in ["search", "find", "what is", "who is", "research"]):
            return f"[Researcher] {self.specialists['researcher'].chat(task)}"
        elif any(w in task_lower for w in ["code", "python", "write", "program", "function"]):
            return f"[Coder] {self.specialists['coder'].chat(task)}"
        elif any(w in task_lower for w in ["write", "essay", "story", "article"]):
            return f"[Writer] {self.specialists['writer'].chat(task)}"
        else:
            return self.main.chat(task)


# =============================================
# Two-Agent Chat (Alice & Bob)
# =============================================
class TwoAgentChat:
    """
    Two agents that can chat with each other.
    """
    
    def __init__(self):
        self.alice = Agent(
            name="Alice",
            role="curious",
            system_prompt="You are Alice, curious and friendly. You like to ask questions."
        )
        self.bob = Agent(
            name="Bob",
            role="knowledgeable",
            system_prompt="You are Bob, knowledgeable and patient. You provide detailed explanations."
        )
        self.current = self.alice
    
    def chat(self, msg):
        return self.current.chat(msg)
    
    def switch(self):
        self.current = self.bob if self.current == self.alice else self.alice
        return f"Switched to {self.current.name}"
    
    def ask_other(self, msg):
        other = self.bob if self.current == self.alice else self.alice
        return other.chat(msg)


# =============================================
# Test
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Step 4: Multi-Agent Collaboration")
    print("=" * 50)
    
    print("""
Two approaches:

1. Specialist Routing:
   - Task -> Main (planner) -> Specialist -> Result
   - Researcher, Coder, Writer

2. Two-Agent Chat:
   - Alice & Bob can talk to each other
   - Can switch between them
   - Can ask the other agent

Examples:
""")
    
    # Demo specialist routing
    print("\n--- Demo 1: Specialist Routing ---")
    system = MultiAgentSystem()
    
    result = system.delegate("What is Python?")
    print(f"Task: What is Python?")
    print(f"Result: {result[:100]}...")
    
    result = system.delegate("Write a hello world function")
    print(f"\nTask: Write hello world")
    print(f"Result: {result[:100]}...")
    
    # Demo two-agent chat
    print("\n--- Demo 2: Two-Agent Chat ---")
    chat = TwoAgentChat()
    print(f"Current: {chat.current.name}")
    print(f"Switch: {chat.switch()}")
    print(f"Current: {chat.current.name}")


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 4 Summary: Multi-Agent Collaboration
==================================================

What we learned:
- Single agent: One LLM does everything
- Multi-agent: Multiple LLMs with different roles
- Collaboration: Agents work together

Architecture:
- Main: Planner (decides what to do)
- Researcher: Finds info
- Coder: Writes code
- Writer: Creates content

Benefits:
- Specialization (each agent is expert)
- Parallel processing (all work on task)
- Better results (multiple perspectives)

Next: Step 5 - Web UI
""")
