"""
step7_deploy.py - Deploy to Cloud

Make the agent accessible online!

Options:
1. Railway (easiest)
2. Render (free tier)
3. Fly.io (good for containers)
4. Hugging Face Spaces (free!)

We'll use a simple Flask deployment that can be deployed anywhere.
"""
import os
import json
import requests

# Copy tools from previous steps
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
    # For cloud, use environment variable or default
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    try:
        response = requests.post(
            f"{ollama_url}/api/chat",
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
# Flask Web App (Deployment-Ready)
# =============================================
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
agent = PiAgent()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pi Agent - Deployed</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        #chat { border: 1px solid #ddd; border-radius: 10px; padding: 20px; background: white; height: 400px; overflow-y: auto; margin-bottom: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #e3f2fd; }
        .agent { background: #f1f8e9; }
        input { width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🤖 Pi Agent - Cloud Deployed</h1>
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
                const response = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: message}) });
                const data = await response.json();
                addMessage('agent', data.response);
            } catch (error) { addMessage('agent', 'Error: ' + error.message); }
        }
        document.getElementById('message').addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
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
    try:
        response = agent.chat(data.get('message', ''))
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

# =============================================
# Deployment Config Files
# =============================================
def create_deployment_files():
    """Create files needed for deployment"""
    
    # requirements.txt
    requirements = """flask
requests
gunicorn
"""
    write("requirements.txt", requirements)
    
    # Dockerfile
    dockerfile = """FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "step7_deploy:app"]
"""
    write("Dockerfile", dockerfile)
    
    # .dockerignore
    dockerignore = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.git
.gitignore
.vscode
.env
*.md
"""
    write(".dockerignore", dockerignore)
    
    # Procfile (for Railway/Render)
    write("Procfile", "web: gunicorn --bind 0.0.0.0:$PORT step7_deploy:app")
    
    print("✅ Created deployment files:")
    print("   - requirements.txt")
    print("   - Dockerfile")
    print("   - .dockerignore")
    print("   - Procfile")


# =============================================
# Test locally first
# =============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Step 7: Deploy to Cloud")
    print("=" * 50)
    
    print("""
Deployment Options:

1. Railway (Easiest)
   - Go to railway.app
   - Connect GitHub
   - Deploy this repo
   - Done!

2. Render (Free tier)
   - Go to render.com
   - Connect GitHub
   - Deploy as Web Service
   - Free!

3. Hugging Face Spaces (Free!)
   - Go to huggingface.co/spaces
   - Create new Space
   - Upload files
   - Done!

4. Fly.io (Container)
   - Install flyctl
   - fly launch
   - fly deploy
""")
    
    # Create deployment files
    create_deployment_files()
    
    print("\n" + "=" * 50)
    print("Testing locally...")
    print("=" * 50)
    
    # Test the agent
    print("\nTesting agent (single message)...")
    result = agent.chat("Say hello in one word")
    print(f"Agent: {result}")
    
    print("\n" + "=" * 50)
    print("To deploy to cloud:")
    print("=" * 50)
    print("""
1. Commit all files to GitHub:
   git add .
   git commit -m "Add deployment"
   git push

2. Deploy on Railway/Render/HuggingFace:
   - Connect your GitHub repo
   - Deploy!

3. Set OLLAMA_URL if using remote Ollama:
   - Railway: Add OLLAMA_URL environment variable
   - Or use local Ollama for local testing
    """)


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 7 Summary: Deploy to Cloud
==================================================

What we created:
- Flask web app (deployment-ready)
- requirements.txt (dependencies)
- Dockerfile (container config)
- Procfile (deployment config)

Deployment options:
1. Railway - Easiest, good free tier
2. Render - Free web service
3. Hugging Face - Completely free!
4. Fly.io - For containers

Key files:
- step7_deploy.py - Main app
- requirements.txt - Python dependencies
- Dockerfile - Container image
- Procfile - Deployment command

Environment variables:
- OLLAMA_URL - URL to your Ollama server (if remote)

Next: Build a real project!
""")