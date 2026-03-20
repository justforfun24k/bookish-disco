import re
import time
import os
import subprocess
import requests
from ddgs import DDGS

class SmartAgent:
    def __init__(self, llm_provider="ollama"):
        self.memory = []          # Conversation history
        self.facts = {}           # Key-value facts
        self.llm_provider = llm_provider
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
            "llm": self.call_llm,
            "read_file": self.read_file,
            "run_code": self.run_code,
            "list_dir": self.list_directory,
            "open_url": self.open_url,
        }
    
    def think(self, user_input):
        self.memory.append(f"User: {user_input}")
        
        print(f"[Thinking...]")
        
        # Multi-step planning for complex tasks
        plan = self.plan(user_input)
        
        print(f"[Plan: {len(plan)} step(s)]")
        
        # Execute plan
        result = self.execute(plan, user_input)
        
        self.memory.append(f"Agent: {result}")
        
        return result
    
    def plan(self, task):
        task_lower = task.lower()
        plan = []
        
        # ========== COMPLEX TASKS → Use LLM for planning ==========
        complex_keywords = [
            "explain", "why", "how does", "write code", "help me", 
            "can you", "what do you think", "your opinion", "describe",
            "compare", "difference between", "create", "build", "make"
        ]
        
        if any(kw in task_lower for kw in complex_keywords):
            # Complex task - use LLM
            plan.append(("tool", "llm", task))
        
        # ========== TOOL-SPECIFIC PLANNING ==========
        
        # Read file: "read file X" or "what's in file X"
        elif "read" in task_lower and ("file" in task_lower or "." in task):
            match = re.search(r'file\s+([^\s]+)|([^\s]+\.(py|txt|json|md|csv|html|css|js))', task_lower)
            if match:
                filename = match.group(1) or match.group(2)
                plan.append(("tool", "read_file", filename))
        
        # List directory: "list files" or "what files"
        elif "list" in task_lower and "file" in task_lower:
            plan.append(("tool", "list_dir", "."))
        
        # Run code: "run X" or "execute X"
        elif "run" in task_lower or "execute" in task_lower or "python" in task_lower:
            if ".py" in task:
                match = re.search(r'([^\s]+\.py)', task)
                if match:
                    plan.append(("tool", "run_code", match.group(1)))
        
        # Open URL: "open website" or "visit"
        elif "open" in task_lower and ("url" in task_lower or "website" in task_lower or "http" in task_lower):
            match = re.search(r'(https?://[^\s]+)', task)
            if match:
                plan.append(("tool", "open_url", match.group(1)))
        
        # ========== FACT MEMORY ==========
        elif "remember" in task_lower or "my name is" in task_lower:
            plan.append(("store_fact", task))
        
        elif "what did i tell you" in task_lower or "what's my name" in task_lower:
            plan.append(("recall_all_facts", None))
        
        # ========== SEARCH (current info) ==========
        elif "what is" in task_lower or "who is" in task_lower or "tell me about" in task_lower:
            query = task_lower.replace("what is", "").replace("who is", "").replace("tell me about", "").replace("?", "").strip()
            # Check facts first
            if query in self.facts:
                plan.append(("recall_fact", query))
            elif query:
                plan.append(("tool", "search", query))
        
        elif "search" in task_lower:
            query = task_lower.replace("search", "").strip()
            if query:
                plan.append(("tool", "search", query))
        
        # ========== CALCULATOR ==========
        elif "calculate" in task_lower or any(op in task for op in ["+", "-", "*", "/", "**"]):
            plan.append(("tool", "calculator", task))
        
        # ========== TIME ==========
        elif "time" in task_lower:
            plan.append(("tool", "time", None))
        
        # ========== WHO ARE YOU ==========
        elif "who are you" in task_lower:
            plan.append(("respond", "I am an AI agent! I can search the web, calculate, tell time, remember facts, read/run code, and use LLM for complex questions."))
        
        # ========== CLEAR MEMORY ==========
        elif "forget" in task_lower or "clear" in task_lower:
            plan.append(("clear_memory", None))
        
        # ========== DEFAULT: Use LLM ==========
        else:
            plan.append(("tool", "llm", task))
        
        return plan
    
    def execute(self, plan, original_task):
        results = []
        
        for i, step in enumerate(plan):
            step_type = step[0]
            
            if step_type == "respond":
                return step[1]
            
            # ========== TOOL EXECUTION ==========
            elif step_type == "tool":
                tool_name = step[1]
                param = step[2]
                
                print(f"  → Step {i+1}: {tool_name}({param})")
                
                if tool_name == "search":
                    param = param.replace("?", "").replace(".", "").strip() if param else ""
                    results.append(self.web_search(param))
                
                elif tool_name == "calculator":
                    try:
                        expr = self.extract_math(original_task)
                        if expr:
                            answer = eval(expr)
                            results.append(f"Calculation: {expr} = {answer}")
                    except Exception as e:
                        results.append(f"Calculation error: {e}")
                
                elif tool_name == "time":
                    results.append(f"Current time: {time.strftime('%H:%M:%S')}")
                
                elif tool_name == "llm":
                    context = "\n".join(self.memory[-6:])
                    results.append(self.call_llm(param, context))
                
                elif tool_name == "read_file":
                    results.append(self.read_file(param))
                
                elif tool_name == "run_code":
                    results.append(self.run_code(param))
                
                elif tool_name == "list_dir":
                    results.append(self.list_directory(param))
                
                elif tool_name == "open_url":
                    results.append(self.open_url(param))
            
            # ========== FACT MEMORY ==========
            elif step_type == "store_fact":
                print(f"  → Step {i+1}: Storing fact...")
                task = original_task.lower()
                
                if "my name is" in task:
                    name = original_task.lower().replace("my name is", "").strip()
                    self.facts["name"] = name.title()
                    results.append(f"Okay! I'll remember your name is {self.facts['name']}")
                
                elif "remember" in task:
                    match = re.search(r'remember (.*?) is (.*)', task)
                    if match:
                        key = match.group(1).strip()
                        value = match.group(2).strip()
                        self.facts[key] = value
                        results.append(f"Okay! I'll remember that {key} is {value}")
                    else:
                        results.append("I didn't understand. Try 'my name is [name]'.")
            
            elif step_type == "recall_fact":
                query = step[1]
                if query in self.facts:
                    results.append(f"{query} is {self.facts[query]}")
                else:
                    results.append(f"I don't know what {query} is.")
            
            elif step_type == "recall_all_facts":
                if self.facts:
                    facts_list = [f"{k}: {v}" for k, v in self.facts.items()]
                    results.append("I remember: " + ", ".join(facts_list))
                else:
                    results.append("I don't remember any facts yet.")
            
            elif step_type == "clear_memory":
                mem_count = len(self.memory)
                fact_count = len(self.facts)
                self.memory = []
                self.facts = {}
                results.append(f"Memory cleared! I forgot {mem_count//2} messages and {fact_count} facts.")
        
        return "\n".join(results) if results else "Done."
    
    def extract_math(self, text):
        expr = re.findall(r'[\d\+\-\*\/\.\%]+', text)
        if expr:
            return "".join(expr)
        return None
    
    # ============ TOOL: SEARCH ============
    def web_search(self, query):
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=3)
            
            if not results:
                return "No results found."
            
            formatted = []
            for r in results:
                title = r.get('title', 'No title')
                body = r.get('body', '')[:150]
                if body:
                    formatted.append(f"📌 {title}\n   {body}...")
                else:
                    formatted.append(f"📌 {title}")
            
            return "\n\n".join(formatted)
        
        except Exception as e:
            return f"Search error: {str(e)}"
    
    # ============ TOOL: READ FILE ============
    def read_file(self, filepath):
        try:
            # Security: only allow certain extensions
            allowed_ext = ['.py', '.txt', '.json', '.md', '.csv', '.html', '.css', '.js', '.txt']
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext not in allowed_ext:
                return f"Error: Cannot read {ext} files. Allowed: {allowed_ext}"
            
            # Get absolute path if relative
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()[:2000]  # Limit to 2000 chars
            
            return f"📄 Content of {filepath}:\n{content}"
        
        except FileNotFoundError:
            return f"Error: File '{filepath}' not found."
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    # ============ TOOL: RUN CODE ============
    def run_code(self, filepath):
        try:
            if not filepath.endswith('.py'):
                return f"Error: Can only run .py files. Got: {filepath}"
            
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            
            # Run the Python file
            result = subprocess.run(
                ['python', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = []
            if result.stdout:
                output.append(f"Output:\n{result.stdout}")
            if result.stderr:
                output.append(f"Errors:\n{result.stderr}")
            
            if not output:
                return "No output."
            
            return "\n".join(output)
        
        except FileNotFoundError:
            return f"Error: File '{filepath}' not found."
        except subprocess.TimeoutExpired:
            return "Error: Code took too long to run (timeout)."
        except Exception as e:
            return f"Error running code: {str(e)}"
    
    # ============ TOOL: LIST DIRECTORY ============
    def list_directory(self, path="."):
        try:
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            
            files = os.listdir(path)
            
            if not files:
                return "Empty directory."
            
            # Separate dirs and files
            dirs = [f + "/" for f in files if os.path.isdir(os.path.join(path, f))]
            files = [f for f in files if not os.path.isdir(os.path.join(path, f))]
            
            result = "📁 Files:\n"
            if dirs:
                result += "Dirs: " + ", ".join(dirs[:10])
            if files:
                result += "\nFiles: " + ", ".join(files[:20])
            
            return result
        
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    # ============ TOOL: OPEN URL ============
    def open_url(self, url):
        return f"🔗 Would open: {url}\n(Browsers cannot be controlled directly - copy this URL to open)"
    
    # ============ LLM ============
    def call_llm(self, prompt, context=""):
        system_prompt = """You are a helpful AI assistant. Be concise and friendly.
You have memory of the conversation."""
        
        try:
            if self.llm_provider == "lmstudio":
                response = requests.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={
                        "model": "local-model",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                    },
                    timeout=300
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    return f"[LM Studio error: {response.status_code}]"
            
            elif self.llm_provider == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "tinyllama",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                    },
                    timeout=200
                )
                if response.status_code == 200:
                    return response.json()["message"]["content"]
                else:
                    return f"[Ollama error: {response.status_code}]"
        
        except requests.exceptions.ConnectionError:
            return "[Error] Cannot connect to LLM. Make sure Ollama/LM Studio is running!"
        except Exception as e:
            return f"[Error] LLM: {str(e)}"
    
    # ============ BASIC TOOLS ============
    def calculate(self, expr):
        try:
            return str(eval(expr))
        except:
            return "Error"
    
    def get_time(self):
        return time.strftime("%H:%M:%S")
    
    def show_memory(self):
        print("\n--- Memory ---")
        for msg in self.memory[-10:]:
            print(msg)
        print(f"\n--- Facts ---")
        for k, v in self.facts.items():
            print(f"  {k}: {v}")
        print("--------------\n")


# ============ MAIN ============
print("=" * 60)
print("Smart Agent v7 - Full Features!")
print("=" * 60)
print("""
Now with more tools:
- search     : Search the web
- calculator : Calculate math
- time       : Get current time  
- llm        : Ask LLM for explanations
- read_file  : Read files (.py, .txt, .json, .md, etc)
- run_code   : Run Python files
- list_dir   : List files in directory
- open_url   : Open URLs
""")

agent = SmartAgent(llm_provider="ollama")

# Interactive mode
print("\n" + "="*60)
print("Interactive Mode - Type 'quit' to exit")
print("="*60)

while True:
    try:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        response = agent.think(user_input)
        print(f"\nAgent: {response}")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break

agent.show_memory()
