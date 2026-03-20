import re
import time
import os
import subprocess
import requests
from ddgs import DDGS

class SmartAgent:
    def __init__(self, llm_provider="ollama"):
        self.memory = []
        self.facts = {}
        self.llm_provider = llm_provider
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
            "llm": self.call_llm,
            "read_file": self.read_file,
            "run_code": self.run_code,
            "list_dir": self.list_directory,
        }
    
    def think(self, user_input):
        self.memory.append(f"User: {user_input}")
        
        print(f"[Thinking...]")
        
        plan = self.plan(user_input)
        print(f"[Plan: {len(plan)} step(s)]")
        
        result = self.execute(plan, user_input)
        
        self.memory.append(f"Agent: {result}")
        return result
    
    def plan(self, task):
        task_lower = task.lower()
        plan = []
        
        # Complex → LLM
        if any(kw in task_lower for kw in ["explain", "why", "how does", "what do you think", "describe", "tell me about"]):
            plan.append(("tool", "llm", task))
        
        # Read file
        elif "read" in task_lower and "file" in task_lower:
            match = re.search(r'file\s+(\S+)|(\S+\.(py|txt|json|md))', task)
            filename = match.group(1) or match.group(2) if match else None
            if filename:
                plan.append(("tool", "read_file", filename))
        
        # List files
        elif "list" in task_lower and "file" in task_lower:
            plan.append(("tool", "list_dir", "."))
        
        # Run code
        elif "run" in task_lower or ".py" in task:
            match = re.search(r'(\S+\.py)', task)
            if match:
                plan.append(("tool", "run_code", match.group(1)))
        
        # Store fact
        elif "remember" in task_lower or "my name is" in task_lower:
            plan.append(("store_fact", task))
        
        # Recall facts
        elif "what did i tell" in task_lower or "what's my name" in task_lower:
            plan.append(("recall_all_facts", None))
        
        # Search (what is / who is)
        elif "what is" in task_lower or "who is" in task_lower:
            query = task_lower.replace("what is", "").replace("who is", "").replace("?", "").strip()
            if query in self.facts:
                plan.append(("recall_fact", query))
            elif query:
                plan.append(("tool", "search", query))
        
        elif "search" in task_lower:
            query = task_lower.replace("search", "").strip()
            if query:
                plan.append(("tool", "search", query))
        
        # Calculate
        elif "calculate" in task_lower or any(op in task for op in ["+", "-", "*", "/", "**"]):
            plan.append(("tool", "calculator", task))
        
        # Time
        elif "time" in task_lower:
            plan.append(("tool", "time", None))
        
        # Who are you
        elif "who are you" in task_lower:
            plan.append(("respond", "I am an AI agent! I can search, read files, run code, calculate, and chat with LLM."))
        
        # Clear memory
        elif "forget" in task_lower or "clear" in task_lower:
            plan.append(("clear_memory", None))
        
        # Default → LLM
        else:
            plan.append(("tool", "llm", task))
        
        return plan
    
    def execute(self, plan, original_task):
        results = []
        
        for i, step in enumerate(plan):
            step_type = step[0]
            
            if step_type == "respond":
                return step[1]
            
            elif step_type == "tool":
                tool_name = step[1]
                param = step[2]
                
                print(f"  → Step {i+1}: {tool_name}")
                
                if tool_name == "search":
                    results.append(self.web_search(param or original_task))
                
                elif tool_name == "calculator":
                    try:
                        expr = self.extract_math(original_task)
                        if expr:
                            results.append(f"Result: {eval(expr)}")
                    except:
                        results.append("Error")
                
                elif tool_name == "time":
                    results.append(f"Time: {time.strftime('%H:%M:%S')}")
                
                elif tool_name == "llm":
                    results.append(self.call_llm(param or original_task))
                
                elif tool_name == "read_file":
                    results.append(self.read_file(param))
                
                elif tool_name == "run_code":
                    results.append(self.run_code(param))
                
                elif tool_name == "list_dir":
                    results.append(self.list_directory(param))
            
            # Facts
            elif step_type == "store_fact":
                task = original_task.lower()
                if "my name is" in task:
                    name = original_task.lower().replace("my name is", "").strip()
                    self.facts["name"] = name.title()
                    results.append(f"Remembered: your name is {name}")
                elif "remember" in task:
                    match = re.search(r'remember (.*?) is (.*)', task)
                    if match:
                        key = match.group(1).strip()
                        value = match.group(2).strip()
                        self.facts[key] = value
                        results.append(f"Remembered: {key} is {value}")
            
            elif step_type == "recall_fact":
                query = step[1]
                results.append(f"{query} is {self.facts.get(query, 'unknown')}")
            
            elif step_type == "recall_all_facts":
                if self.facts:
                    results.append("Facts: " + ", ".join(f"{k}: {v}" for k,v in self.facts.items()))
                else:
                    results.append("No facts stored.")
            
            elif step_type == "clear_memory":
                self.memory = []
                self.facts = {}
                results.append("Memory cleared.")
        
        return "\n".join(results) if results else "Done."
    
    def extract_math(self, text):
        expr = re.findall(r'[\d\+\-\*\/\.\%]+', text)
        return "".join(expr) if expr else None
    
    # ============ TOOLS ============
    def web_search(self, query):
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=3)
            if not results:
                return "No results."
            return "\n".join(f"{r.get('title','')}: {r.get('body','')[:100]}..." for r in results)
        except Exception as e:
            return f"Error: {e}"
    
    def read_file(self, filepath):
        try:
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()[:2000]
        except FileNotFoundError:
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error: {e}"
    
    def run_code(self, filepath):
        try:
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=30)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def list_directory(self, path="."):
        try:
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            files = os.listdir(path)
            return ", ".join(files[:20])
        except Exception as e:
            return f"Error: {e}"
    
    def calculate(self, expr):
        try:
            return str(eval(expr))
        except:
            return "Error"
    
    def get_time(self):
        return time.strftime("%H:%M:%S")
    
    # ============ LLM ============
    def call_llm(self, prompt):
        system_prompt = "You are a helpful AI assistant. Be concise and friendly."
        
        try:
            if self.llm_provider == "ollama":
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
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json()["message"]["content"]
                else:
                    return f"[Error: {response.status_code}]"
        except Exception as e:
            return f"[Error: {e}]"


# ============ MAIN ============
print("=" * 60)
print("Smart Agent - Working Version!")
print("=" * 60)

agent = SmartAgent(llm_provider="ollama")

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
