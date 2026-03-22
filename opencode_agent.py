"""
opencode_agent.py - Multi-Agent Collaboration

Two or more agents working together.

Simple concept:
- Agent A asks Agent B for help
- Each agent has different role/specialty
- They share results
"""
import json
import requests
import os
import subprocess

# =============================================
# Pi-style Tools (4 core tools)
# =============================================
def read(filepath, limit=100, offset=0):
    """Read a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        total = len(lines)
        selected = lines[offset:offset+limit]
        return {
            "ok": True,
            "content": "".join(selected),
            "total_lines": total,
            "showing": f"lines {offset+1}-{offset+len(selected)}"
        }
    except FileNotFoundError:
        return {"ok": False, "error": f"File not found: {filepath}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def write(filepath, content):
    """Write content to a file."""
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"ok": True, "filepath": filepath}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def edit(filepath, old_string, new_string):
    """Edit a file by replacing old_string with new_string."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if old_string not in content:
            return {"ok": False, "error": "String not found in file"}
        new_content = content.replace(old_string, new_string)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {"ok": True, "filepath": filepath}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def bash(command, timeout=30):
    """Run a shell command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": True, "stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
#=============================================
class Session:
    def __init__(self,session_dir="sessions"):
        self.session_dir=session_dir
        self.messages_file=f"{session_dir}/messages.json"
        self.context_file=f"{session_dir}/context.md"
        self.todos_file=f"{session_dir}/todos.md"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        if not os.path.exists(self.messages_file):
            write(self.messages_file,"[]")
        if not os.path.exists(self.context_file):
            write(self.context_file,"# Context\n\n")
        if not os.path.exists(self.todos_file):
            write(self.todos_file,"# TODOS\n\n- [ ] \n")

    def load_messages(self):
        try:
            with open(self.messages_file,'r',encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    def save_messages(self,messages):
        with open(self.messages_file,'w',encoding='utf-8') as f:
            json.dump(messages,f,ensure_ascii=False,indent=2)
    def add_message(self,role,content):
        messages=self.load_messages()
        messages.append({"role": role,"content": content})
        self.save_messages(messages)
        return len(messages)
    def load_context(self):
        try:
            with open(self.context_file,'r',encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    def update_context(self,content):
        write(self.context_file,content)
    def load_todos(self):
        try:
            with open(self.todos_file,'r',encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    def update_todos(self,content):
        write(self.todos_file,content)
    def new_session(self):
        """Start a new session (clears messages only)."""
        self.save_messages([])
        print("New session started. Messages cleared,context and todos preserved.")

def execute_tool(tool_name,args):
    if tool_name=="read":
        return read(**args)
    elif tool_name=="write":
        return write(**args)
    elif tool_name=="edit":
        return edit(**args)
    elif tool_name=="bash":
        return bash(**args)
    else:
        return({"ok":False,"error": f"Unknown tool: {tool_name}"})
# =============================================
# LLM Connection
# =============================================
def call_llm(messages, model="llama3.2:3b"):
    """Call Ollama LLM"""
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=150
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"


# =============================================
# Base Agent
# =============================================
coder_system_prompt = """You are a coding expert.
 Write clean Python code.
 You are also a helpful coding assistant 
 with access to 4 tools:

1. read(filepath, limit, offset) - Read a file
2. write(filepath, content) - Write to a file  
3. edit(filepath, old_string, new_string) - Edit a file
4. bash(command) - Run a shell command

Guidelines:
- Use read before editing files
- Use edit for precise changes
- Use write for new files or complete rewrites
- Use bash for file operations (ls, grep, find)
- Be concise in responses
- Show file paths clearly
- apply tool in this format,for example:
  <tool>{"tool": "read","args": {...}}</tool>

"""

class Agent:
    """Simple agent with role and chat capability"""
    
    def __init__(self, name, role, system_prompt, model="llama3.2:3b"):
        self.name = name
        self.role = role
        self.model = model
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
    
    def chat(self, user_input):
        """Chat with this agent"""
        self.messages.append({"role": "user", "content": user_input})
        response = call_llm(self.messages, self.model)
        self.messages.append({"role": "assistant", "content": response})
        return response


# =============================================
# Multi-Agent System (Specialists)
# =============================================

class PiAgent:
    def __init__(self,name,role,system_prompt,session_dir="sessions",model="llama3.2:3b"):
        self.name = name
        self.role = role
        self.session=Session(session_dir)
        self.model=model
        self.messages=[{"role": self.role, "content": system_prompt}]
        context=self.session.load_context()
        if context:
            self.messages.append({
                "role": "system",
                "content": f"Current context:\n{context}"
            })
    def chat(self,user_input):
        self.messages.append({"role": "user","content": user_input})
        self.session.add_message("user",user_input)
        response=call_llm(self.messages,self.model)
        if "<tool>" in response and "</tool>" in response:
            start=response.find("<tool>")+6
            end=response.find("</tool>")
            tool_json=response[start:end].strip()
        try:
            tool_call=json.loads(tool_json)
            tool_name=tool_call.get('tool')
            args=tool_call.get('args',{})
            result=execute_tool(tool_name,args)
            self.messages.append({"role": "assistant","content": f"{response}"})
            # Might need to convert dict to string properly:
            tool_output = str(result) if isinstance(result, dict) else result
            self.messages.append({
                "role": "user", 
                "content": f"<tool_result>{tool_output}</tool_result>"
            })
            response=call_llm(self.messages,self.model)
        except Exception as e:
            print(f"Tool error: {e}")
        self.messages.append({"role": "assistant","content": response})
        self.session.add_message("assistant",response)
        return response

class MultiAgentSystem:
    """
    Main agent + Specialist agents.
    
    Architecture:
    User → Main (planner) → Specialist → Result
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
                system_prompt="You are a research expert. Find and summarize information."
            ),
            "coder": PiAgent(
                name="Coder",
                role="coding",
                system_prompt=coder_system_prompt
            ),
            "writer": Agent(
                name="Writer",
                role="writing",
                system_prompt="You are a creative writer. Write engaging content."
            ),
        }
    
    def delegate(self, task):
        """Route task to appropriate specialist"""
        task_lower = task.lower()
        
        if any(w in task_lower for w in ["search", "find", "what is", "who is"]):
            return f"[Researcher] {self.specialists['researcher'].chat(task)}"
        elif any(w in task_lower for w in ["code", "python", "write", "program"]):
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
            system_prompt="You are Alice, curious and friendly."
        )
        self.bob = Agent(
            name="Bob",
            role="knowledgeable",
            system_prompt="You are Bob, knowledgeable and patient."
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
# Demo
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Multi-Agent Collaboration Demo")
    print("=" * 50)
    
    print("""
Multi-Agent Concepts:

1. Single Agent: One LLM does everything
2. Multi-Agent: Multiple LLMs with different roles
3. Collaboration: Agents work together

Architecture:
- Main: Planner (decides what to do)
- Researcher: Finds info
- Coder: Writes code
- Writer: Creates content

Try:
system = MultiAgentSystem()
system.delegate("What is Python?")  # → Researcher
system.delegate("Write hello world")  # → Coder

Or:
chat = TwoAgentChat()
chat.chat("Hello!")
chat.switch()
chat.chat("What's up?")
    """)

system = MultiAgentSystem()
system.delegate("What is Python?")  # → Researcher
system.delegate("Code a simple hello world program")  # → Coder