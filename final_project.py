"""
final_project.py - Personal AI Tutor

A document Q&A system that:
1. Reads your files/documents
2. Stores in vector DB for semantic search
3. Answers questions about them
4. Explains concepts when asked

Combines everything: tools, LLM, session, vector DB, web UI
"""
import os
import json
import subprocess
import requests
from flask import Flask, render_template_string, request, jsonify

# =============================================
# STEP 1: 4 Core Tools (Pi-style)
# =============================================
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
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def search(query, max_results=3):
    """Search the web for information"""
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        if results:
            return {"ok": True, "results": [
                {"title": r.get("title", ""), "body": r.get("body", "")[:200]}
                for r in results
            ]}
        return {"ok": False, "error": "No results found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def execute_tool(tool_name, args):
    if tool_name == "read": return read(**args)
    elif tool_name == "write": return write(**args)
    elif tool_name == "edit": return edit(**args)
    elif tool_name == "bash": return bash(**args)
    elif tool_name == "search": return search(**args)
    else: return {"ok": False, "error": f"Unknown tool: {tool_name}"}


# =============================================
# STEP 3: Session (State in Files)
# =============================================
class Session:
    def __init__(self, session_dir="sessions"):
        self.session_dir = session_dir
        self.messages_file = f"{session_dir}/messages.json"
        self.context_file = f"{session_dir}/context.md"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        if not os.path.exists(self.messages_file):
            write(self.messages_file, "[]")
        if not os.path.exists(self.context_file):
            write(self.context_file, "# Context\n\n")
    
    def load_messages(self):
        try:
            with open(self.messages_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_messages(self, messages):
        with open(self.messages_file, 'w') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def add_message(self, role, content):
        messages = self.load_messages()
        messages.append({"role": role, "content": content})
        self.save_messages(messages)


# =============================================
# STEP 6: Vector Memory (Simplified)
# =============================================
class VectorMemory:
    """Simple vector memory using file-based storage"""
    
    def __init__(self, data_dir="knowledge"):
        self.data_dir = data_dir
        self.index_file = f"{data_dir}/index.json"
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Load or create index
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = []
    
    def add(self, text, source="unknown"):
        """Add a document to memory"""
        # Simple embedding: hash-based for demo
        # Real implementation would use proper embeddings
        import hashlib
        doc_id = hashlib.md5(text.encode()).hexdigest()[:8]
        
        doc = {
            "id": doc_id,
            "source": source,
            "text": text[:1000],  # Store first 1000 chars
            "length": len(text)
        }
        
        self.index.append(doc)
        
        # Save to file
        with open(f"{self.data_dir}/{doc_id}.txt", 'w') as f:
            f.write(text)
        
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f)
        
        return doc_id
    
    def search(self, query, n=3):
        """Simple keyword-based search (demo)"""
        query_lower = query.lower()
        results = []
        
        for doc in self.index:
            # Simple scoring based on word matches
            text_lower = doc["text"].lower()
            score = sum(1 for word in query_lower.split() if word in text_lower)
            
            if score > 0:
                results.append({
                    "source": doc["source"],
                    "text": doc["text"][:200] + "...",
                    "score": score
                })
        
        # Sort by score and return top n
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:n]
    
    def ingest_directory(self, directory):
        """Ingest all files from a directory"""
        import glob
        
        files = glob.glob(f"{directory}/**/*", recursive=True)
        added = 0
        
        for filepath in files:
            if os.path.isfile(filepath) and not filepath.endswith('.pyc'):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 50:  # Skip very short files
                        self.add(content, source=filepath)
                        added += 1
                except:
                    pass
        
        return added


# =============================================
# LLM Connection
# =============================================
def call_llm(messages, model="llama3.2:3b"):
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


# =============================================
# System Prompt
# =============================================
SYSTEM_PROMPT = """You are a helpful learning assistant and coding tutor.

You have access to 5 tools:
1. read(filepath, limit, offset) - Read a file
2. write(filepath, content) - Write to a file
3. edit(filepath, old_string, new_string) - Edit a file
4. bash(command) - Run a shell command
5. search(query, max_results) - Search the web for information

You also have access to your knowledge base - documents and files that have been indexed.

When user asks about code:
- Read the relevant files first
- Explain what the code does
- Suggest improvements

When user asks to learn something:
- Search your knowledge base first
- If not found, search the web
- Explain the concepts clearly

When user asks about recent events or things you don't know:
- Use search to find up-to-date information

Be patient and thorough in your explanations."""


# =============================================
# Main Agent
# =============================================
class PersonalTutor:
    """Personal AI Tutor with document Q&A"""
    
    def __init__(self):
        self.session = Session()
        self.vector_memory = VectorMemory()
        self.model = os.environ.get("MODEL", "llama3.2:3b")
        
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add context from files
        context = self.session.load_messages()
        if context:
            # Add last few messages as context
            recent = context[-3:] if len(context) > 3 else context
            context_text = "\n".join([f"{m['role']}: {m['content'][:100]}" for m in recent])
            self.messages.append({
                "role": "system",
                "content": f"Recent conversation:\n{context_text}"
            })
    
    def chat(self, user_input):
        """Chat with the tutor"""
        # First, search knowledge base if relevant
        knowledge_searched = False
        if any(word in user_input.lower() for word in ["what", "how", "explain", "learn", "code", "file"]):
            knowledge = self.vector_memory.search(user_input, n=2)
            if knowledge:
                knowledge_searched = True
                knowledge_text = "\n\nRelevant from your files:\n" + \
                    "\n".join([f"From {k['source']}: {k['text']}" for k in knowledge])
                self.messages.append({
                    "role": "system",
                    "content": knowledge_text
                })
        
        # If not found in knowledge base, search the web
        if not knowledge_searched and any(word in user_input.lower() for word in ["what is", "how does", "explain", "latest", "recent", "news"]):
            web_results = search(user_input, max_results=2)
            if web_results.get("ok"):
                web_text = "\n\nWeb search results:\n" + \
                    "\n".join([f"• {r['title']}: {r['body']}" for r in web_results.get("results", [])])
                self.messages.append({
                    "role": "system",
                    "content": web_text
                })
        
        # Add user message
        self.messages.append({"role": "user", "content": user_input})
        self.session.add_message("user", user_input)
        
        # Get LLM response
        response = call_llm(self.messages, self.model)
        
        # Check for tool call
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
        self.session.add_message("assistant", response)
        
        return response
    
    def ingest_files(self, directory):
        """Ingest files from a directory"""
        added = self.vector_memory.ingest_directory(directory)
        return f"Added {added} files to knowledge base"
    
    def get_knowledge_count(self):
        """Get number of documents in knowledge base"""
        return len(self.vector_memory.index)


# =============================================
# Flask Web App
# =============================================
app = Flask(__name__)
tutor = PersonalTutor()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Personal AI Tutor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f0f8ff; }
        h1 { color: #2c3e50; text-align: center; }
        .info { background: #e8f4f8; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        #chat { border: 1px solid #bdc3c7; border-radius: 10px; padding: 20px; background: white; height: 450px; overflow-y: auto; margin-bottom: 10px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background: #3498db; color: white; }
        .agent { background: #2ecc71; color: white; }
        input { width: 70%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px; }
        button { padding: 10px 20px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .ingest { background: #9b59b6; }
    </style>
</head>
<body>
    <h1>📚 Personal AI Tutor</h1>
    <div class="info">
        <strong>Knowledge Base:</strong> <span id="kb_count">0</span> documents |
        <strong>Session:</strong> <span id="session_count">0</span> messages
    </div>
    <div id="chat"></div>
    <input type="text" id="message" placeholder="Ask me about your code or files..." autofocus>
    <button onclick="sendMessage()">Send</button>
    <button class="ingest" onclick="ingestFiles()">Ingest Files</button>
    <script>
        function addMessage(role, content) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerHTML = '<strong>' + (role === 'user' ? 'You' : 'Tutor') + ':</strong><br>' + content.replace(/\\n/g, '<br>');
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
                updateInfo();
            } catch (error) {
                addMessage('agent', 'Error: ' + error.message);
            }
        }
        
        async function ingestFiles() {
            const path = prompt('Enter directory path to ingest (e.g., ./my_code):');
            if (!path) return;
            
            try {
                const response = await fetch('/ingest', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: path})
                });
                const data = await response.json();
                addMessage('agent', data.result);
                updateInfo();
            } catch (error) {
                addMessage('agent', 'Error: ' + error.message);
            }
        }
        
        async function updateInfo() {
            const response = await fetch('/info');
            const data = await response.json();
            document.getElementById('kb_count').innerText = data.knowledge_count;
            document.getElementById('session_count').innerText = data.session_messages;
        }
        
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        
        updateInfo();
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
        response = tutor.chat(data.get('message', ''))
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {e}'})

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    path = data.get('path', '')
    try:
        result = tutor.ingest_files(path)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': f'Error: {e}'})

@app.route('/info')
def info():
    return jsonify({
        'knowledge_count': tutor.get_knowledge_count(),
        'session_messages': len(tutor.session.load_messages())
    })


# =============================================
# Main
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🎓 PERSONAL AI TUTOR - FINAL PROJECT")
    print("=" * 60)
    print("""
Features:
✅ Ask questions about your code
✅ Reads files and explains them
✅ Stores knowledge in vector memory
✅ Session history preserved
✅ Web interface

Commands:
- Ask about files: "What does step3_session.py do?"
- Learn concepts: "Explain embeddings"
- Write code: "Write a hello world function"

To ingest your files:
- Click "Ingest Files" button
- Or use: ./your_code_directory

To deploy:
- python final_project.py
- Open http://127.0.0.1:5000
    """)
    
    # Pre-load some knowledge
    print("\nIngesting step files as sample knowledge...")
    tutor.ingest_files(".")
    print(f"Knowledge base: {tutor.get_knowledge_count()} documents")
    
    print("\nStarting server...")
    app.run(debug=True, port=5000)


# =============================================
# Summary
# =============================================
print("""
==================================================
FINAL PROJECT SUMMARY
==================================================

What we built:
1. 4 core tools (Pi-style)
2. LLM connection (Ollama)
3. Session/memory (files)
4. Multi-agent capability
5. Web UI (Flask)
6. Vector memory (knowledge base)
7. Cloud deployment ready

Personal AI Tutor can:
- Answer questions about your code
- Explain concepts
- Remember past conversations
- Ingest new files/documents
- Work as a web app

This combines everything we learned!
""")