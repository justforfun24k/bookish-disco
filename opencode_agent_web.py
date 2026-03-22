"""
opencode_agent_web.py - Web UI for Pi-Style Agent

A simple web interface to chat with the agent.
"""
from flask import Flask, render_template_string, request, jsonify
from opencode_agent import PiAgent

app = Flask(__name__)

# Create agent
SYSTEM_PROMPT = """You are a helpful coding assistant with access to 4 tools:

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

State is stored in files:
- TODOs in todos.md
- Context in context.md
- Conversation in messages.json"""

agent = PiAgent(name="PiAgent", role="system", system_prompt=SYSTEM_PROMPT, session_dir="session")

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
        .error { color: red; }
        .info { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🤖 Pi-Style Agent</h1>
    <p class="info">Type a message to chat with the agent. Type 'new' to start a new session.</p>
    
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
        
        // Send on Enter
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Show the chat interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    message = data.get('message', '')
    
    try:
        response = agent.chat(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

if __name__ == '__main__':
    print("=" * 50)
    print("Pi-Style Agent Web UI")
    print("=" * 50)
    print("Open browser to: http://127.0.0.1:5000")
    print()
    app.run(debug=True, port=5000)
