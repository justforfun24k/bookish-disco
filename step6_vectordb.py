"""
step6_vectordb.py - Vector Database for Long-Term Memory

Vector databases store "embeddings" - numerical representations of text.
This allows semantic search - finding similar ideas, not just keywords.

Example:
- "cat" and "kitten" have similar embeddings
- "apple" and "fruit" are related
- Search "pet" could find "cat" even if "pet" isn't in the text

We'll use ChromaDB - simple and works locally.
"""
import os
import json
import requests

# Install chromadb: pip install chromadb

# =============================================
# 4 Tools (from step1)
# =============================================
def read(filepath, limit=100, offset=0):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        total = len(lines)
        selected = lines[offset:offset+limit]
        return {"ok": True, "content": "".join(selected), "total_lines": total}
    except FileNotFoundError:
        return {"ok": False, "error": f"File not found: {filepath}"}
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
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =============================================
# Vector Database (ChromaDB)
# =============================================
print("=" * 50)
print("Step 6: Vector Database for Long-Term Memory")
print("=" * 50)

print("""
What is a Vector Database?

Normal database: Store exact text
Vector database: Store numerical representations (embeddings)

Why useful?
- Semantic search: Find "similar" ideas
- "What did we discuss about Python?" → finds all Python-related notes
- Even if you don't mention "Python" directly

Example:
- User asks: "What did I learn about neural networks?"
- Vector search finds: notes containing "neural", "network", "deep learning"
- Without vector search: would only find exact "neural networks" match
""")

# Check if chromadb is installed
try:
    import chromadb
    print("\n✅ ChromaDB is installed!")
except ImportError:
    print("\n❌ ChromaDB not installed")
    print("Install with: pip install chromadb")
    print("Skipping vector DB demo...\n")


class VectorMemory:
    """
    Long-term memory using ChromaDB.
    
    Stores conversations as embeddings.
    Allows semantic search across all past conversations.
    """
    
    def __init__(self, persist_dir="vector_memory"):
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.Client(Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            ))
            self.collection = self.client.create_collection("memory")
            self.embeddings = []  # Store original texts
            print(f"✅ Vector memory initialized at {persist_dir}")
        except Exception as e:
            print(f"❌ Vector memory error: {e}")
            self.client = None
            self.collection = None
    
    def add(self, text, metadata=None):
        """Add a memory"""
        if not self.collection:
            return False
        
        try:
            # Generate a simple embedding (for demo)
            # In production, use OpenAI or local embeddings
            embedding = self._simple_embed(text)
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                ids=[f"memory_{len(self.embeddings)}"]
            )
            self.embeddings.append(text)
            return True
        except Exception as e:
            print(f"Add error: {e}")
            return False
    
    def search(self, query, n_results=3):
        """Search memories semantically"""
        if not self.collection:
            return []
        
        try:
            query_embedding = self._simple_embed(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results.get('documents', [[]])[0]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _simple_embed(self, text):
        """Simple embedding for demo (use real embeddings in production)"""
        # This is a VERY simple embedding - just character frequency
        # For real use, integrate with OpenAI embeddings or local model
        import hashlib
        # Create a pseudo-embedding from text hash
        embedding = [0] * 10
        for i, char in enumerate(text[:10]):
            embedding[i % 10] += ord(char)
        # Normalize
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
        return embedding


class Session:
    """Session from step3 - state in files"""
    def __init__(self, session_dir="sessions"):
        self.session_dir = session_dir
        self.messages_file = f"{session_dir}/messages.json"
        self.context_file = f"{session_dir}/context.md"
        self.todos_file = f"{session_dir}/todos.md"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
        if not os.path.exists(self.messages_file):
            write(self.messages_file, "[]")
        if not os.path.exists(self.context_file):
            write(self.context_file, "# Context\n\n")
        if not os.path.exists(self.todos_file):
            write(self.todos_file, "# TODOs\n\n- [ ] \n")
    
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


class PiAgentWithMemory:
    """
    Pi-style agent with both session and vector memory.
    
    Session memory: Current conversation (short-term)
    Vector memory: All past conversations (long-term)
    """
    
    def __init__(self):
        self.session = Session()
        self.vector_memory = VectorMemory()
        
        # System prompt with memory access
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

You have long-term memory (vector database). When user asks about past topics, search your memory."""

        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    def chat(self, user_input):
        # Check vector memory for relevant past conversations
        if any(word in user_input.lower() for word in ["remember", "past", "before", "learned", "discussed"]):
            past_memories = self.vector_memory.search(user_input, n_results=3)
            if past_memories:
                memory_context = "\n\nPast relevant memories:\n" + "\n".join(f"- {m}" for m in past_memories)
                self.messages.append({
                    "role": "system",
                    "content": f"Relevant past: {memory_context}"
                })
        
        # Normal chat
        self.messages.append({"role": "user", "content": user_input})
        self.session.add_message("user", user_input)
        
        # Call LLM
        response = self._call_llm()
        
        self.messages.append({"role": "assistant", "content": response})
        self.session.add_message("assistant", response)
        
        # Save to vector memory
        self.vector_memory.add(f"User: {user_input}\nAssistant: {response}")
        
        return response
    
    def _call_llm(self):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": "llama3.2:3b", "messages": self.messages, "stream": False},
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["message"]["content"]
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"LLM Error: {e}"


# =============================================
# Demo
# =============================================
if __name__ == "__main__":
    print("""
Vector Database Features:

1. add(text) - Store a memory
2. search(query, n_results) - Find similar memories

Example workflow:
1. "I learned about neural networks today"
2. "What did I learn about neural networks?"
3. → Finds the previous neural network conversation

This is different from session memory:
- Session: Current conversation only
- Vector: ALL past conversations, searchable

Try it in your agent!
    """)


# =============================================
# Summary
# =============================================
print("""
==================================================
Step 6 Summary: Vector Database
==================================================

What we learned:
- Vector databases store embeddings (numerical text representations)
- Enables semantic search (find similar ideas, not just keywords)
- ChromaDB is simple and works locally
- Long-term memory vs session memory

Why useful?
- Agent can recall past discussions
- "What did we discuss about Python?" → finds all Python notes
- Doesn't need exact keywords to match

Integration:
- Add important conversations to vector DB
- When user asks, search vector DB first
- Feed relevant memories to LLM context

Next steps could be:
- Add real embeddings (OpenAI or local model)
- Store file changes
- Track learning progress
""")
