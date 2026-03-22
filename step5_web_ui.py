"""
step5_web_ui.py - Web UI for Pi-Style Agent

Builds on step3_session.py
Adds a browser interface

Step 1: 4 tools
Step 2: Connect to LLM
Step 3: Session/memory
Step 4: Multi-agent
Step 5: Web UI
"""
from flask import Flask, render_template_string, request, jsonify
import json
import requests
import os

# Copy tools from step1
def read(filepath, limit=100, offset=0):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return {"ok": True, "content": "".join(lines[offset:offset+limit]), "total_lines": len(lines)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def write(filepath, content):
    try:
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

SYSTEM_PROMPT = """You are a helpful coding assistant with access to 4 tools:

1. read(filepath, limit, offset) - Read a file
2. write(filepath, content) - Write to a file
3. edit(filepath, old_string, new_string) - Edit a file
4. bash(command) - Run a shell command

Guidelines:
- Use read before editing files
- Use edit for precise changes
- Use write for new files
- Be concise in responses"""

class PiAgent:
    def __init__(self, model="llama3.2:3b"):
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        response = call_llm(self.messages, self.model)
        
        if "<tool>" in response and "</tool>" in response:
            start = response.find("<tool>") + 6
            end = response.find("</tool>")
            tool_json = response[start:end].strip()
            
            try:
                tool_call = json.loads(tool_json)
                tool_name = tool_call.get("tool")
                args = tool_call.get("args", {})
                result = execute_tool(tool_name, args)
                
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({"role": "user", "content": f"<tool_result>{result}</tool_result>"})
                response = call_llm(self.messages, self.model)
            except Exception as e:
                print(f"Tool error: {e}")
        
        self.messages.append({"role": "assistant", "content": response})
        return response

# =============================================
# Flask Web App
# =============================================
app = Flask(__name__)

# Create agent
agent = PiAgent()

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pi-Style Agent</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        #chat {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            background: white;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; }
        .agent { background: #f1f8e9; }
        input { 
            width: 70%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
        }
        button { 
            padding: 10px 20px; 
            background: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>Pi-Style Agent</h1>
    <p>Chat with your coding assistant</p>
    
    <div id="chat"></div>
    
    <input type="text" id="message" placeholder="Type your message..." autofocus>
    <button onclick="sendMessage()">Send</button>
    
    <script>
        function addMessage(role, content) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerHTML = '<strong>' + (role === 'user' ? 'You' : 'Agent') + ':</strong> ' + content;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        async function sendMessage() {
            const input = document.getElementById('message');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage('user', message);
            input.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                addMessage('agent', data.response);
            } catch (error) {
                addMessage('agent', 'Error: ' + error.message);
            }
        }
        
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    try:
        response = agent.chat(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

# =============================================
# Main
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Step 5: Web UI")
    print("=" * 50)
    print()
    print("Open browser to: http://127.0.0.1:5000")
    print()
    app.run(debug=True, port=5000)


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 5 Summary: Web UI
==================================================

What we added:
- Flask web framework
- Browser interface
- Real-time chat

How it works:
1. Flask runs web server on port 5000
2. Browser shows chat interface
3. User types message
4. JS sends to /chat endpoint
5. Agent processes and returns response
6. JS displays response

To run:
1. pip install flask
2. python step5_web_ui.py
3. Open http://127.0.0.1:5000

Next: Step 6 - Vector Database
""")
