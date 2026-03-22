"""
step2_llm.py - Connect to LLM

Builds on step1_basics.py
Adds LLM connection to make it an "agent"

Step 1: 4 tools (read, write, edit, bash)
Step 2: Connect tools to LLM
"""
import os
import subprocess
import requests

# Copy tools from step1
def read(filepath, limit=100, offset=0):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        total = len(lines)
        selected = lines[offset:offset+limit]
        return {"ok": True, "content": "".join(selected), "total_lines": total}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def write(filepath, content):
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
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if old_string not in content:
            return {"ok": False, "error": "String not found"}
        new_content = content.replace(old_string, new_string)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {"ok": True, "filepath": filepath}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def bash(command, timeout=30):
    try:
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

# =============================================
# LLM Connection (Ollama)
# =============================================
def call_llm(messages, model="llama3.2:3b"):
    """
    Call local Ollama LLM.
    
    Args:
        messages: List of message dicts [{"role": "user", "content": "..."}]
        model: Model name (default llama3.2:3b)
    
    Returns:
        LLM response text
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# =============================================
# System Prompt (Pi-style - minimal)
# =============================================
SYSTEM_PROMPT = """You are a helpful coding assistant with access to 4 tools:

1. read(filepath, limit, offset) - Read a file
2. write(filepath, content) - Write to a file
3. edit(filepath, old_string, new_string) - Edit a file
4. bash(command) - Run a shell command

Guidelines:
- Use read before editing files
- Use edit for precise changes
- Use write for new files
- Use bash for commands (ls, grep, find)
- Be concise in responses"""

# =============================================
# Simple Agent
# =============================================
class SimpleAgent:
    """Simple agent with 4 tools + LLM brain"""
    
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def chat(self, user_input):
        """Chat with the agent"""
        # Add user message
        self.messages.append({"role": "user", "content": user_input})
        
        # Get LLM response
        response = call_llm(self.messages, self.model)
        
        # Check for tool call
        if "<tool>" in response and "</tool>" in response:
            start = response.find("<tool>") + 6
            end = response.find("</tool>")
            tool_json = response[start:end].strip()
            
            try:
                import json
                tool_call = json.loads(tool_json)
                tool_name = tool_call.get("tool")
                args = tool_call.get("args", {})
                
                # Execute tool
                result = execute_tool(tool_name, args)
                
                # Add to history
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({
                    "role": "user",
                    "content": f"<tool_result>{result}</tool_result>"
                })
                
                # Get final response
                response = call_llm(self.messages, self.model)
                
            except Exception as e:
                print(f"Tool error: {e}")
        
        # Save response
        self.messages.append({"role": "assistant", "content": response})
        return response


# =============================================
# Test
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Step 2: Connect to LLM")
    print("=" * 50)
    
    # Test LLM connection
    print("\n1. Test LLM connection:")
    test_messages = [{"role": "user", "content": "Say 'Hello' in one word"}]
    response = call_llm(test_messages)
    print(f"   LLM says: {response}")
    
    # Create agent
    print("\n2. Create agent:")
    agent = SimpleAgent()
    print(f"   Agent created with model: {agent.model}")
    
    # Test chat
    print("\n3. Test chat (type 'quit' to exit):")
    print("   Try: 'What is Python?'")
    print("   Try: 'Read the file step2_llm.py'")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        
        response = agent.chat(user_input)
        print(f"\nAgent: {response}")


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 2 Summary: Connect to LLM
==================================================

What we added:
- call_llm() - Connect to Ollama
- SYSTEM_PROMPT - Minimal instructions
- SimpleAgent class - Combines tools + LLM

How it works:
1. User sends message
2. LLM analyzes and decides if to use tool
3. If tool needed → returns <tool> format
4. We execute tool → return result
5. LLM gives final response

Key insight:
- LLM decides WHEN to use tools
- We just provide the tools
- LLM is the "brain"

Next: Step 3 - Session/Memory (state in files)
""")
