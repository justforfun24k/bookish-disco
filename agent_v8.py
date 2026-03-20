import re
import time
import os
import subprocess
import requests
from ddgs import DDGS

class AutonomousAgent:
    def __init__(self, llm_provider="ollama", max_iterations=5):
        self.memory = []          # Conversation history
        self.facts = {}           # Key-value facts
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations  # Prevent infinite loops
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
            "llm": self.call_llm,
            "read_file": self.read_file,
            "run_code": self.run_code,
            "list_dir": self.list_directory,
            "open_url": self.open_url,
            "finish": self.finish_task,
        }
    
    def think(self, user_input, autonomous=False):
        self.memory.append(f"User: {user_input}")
        
        if not autonomous:
            # Single step mode
            print(f"[Thinking...]")
            plan = self.plan(user_input)
            print(f"[Plan: {len(plan)} step(s)]")
            result = self.execute(plan, user_input)
            self.memory.append(f"Agent: {result}")
            return result
        
        else:
            # Autonomous mode - loop until done
            return self.autonomous_loop(user_input)
    
    def autonomous_loop(self, task):
        """Agent thinks, acts, observes, and repeats until done"""
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS MODE: {task}")
        print(f"{'='*60}\n")
        
        context = f"Task: {task}\n"
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n[Iteration {iteration}/{self.max_iterations}]")
            
            # 1. Think - decide what to do
            action = self.decide_action(task, context)
            print(f"  Decision: {action['type']} - {action.get('detail', '')}")
            
            # 2. Execute the action
            if action['type'] == 'finish':
                result = action.get('response', 'Task completed!')
                print(f"  → Result: {result[:100]}...")
                break
            
            result = self.execute_action(action, task)
            print(f"  → Result: {result[:150]}...")
            
            # 3. Observe - add to context
            context += f"Observation {iteration}: {result}\n"
            
            # 4. Check if done
            if self.is_task_done(task, result):
                print(f"\n[Task appears to be done!]")
                break
        
        if iteration >= self.max_iterations:
            result = f"Reached max iterations ({self.max_iterations}). Last result: {result}"
        
        self.memory.append(f"Agent: {result}")
        return result
    
    def decide_action(self, task, context):
        """Use LLM to decide next action"""
        
        # Build prompt for action selection
        prompt = f"""You are an autonomous AI agent. Given the task and observations, decide the next action.

Task: {task}

Observations so far:
{context}

Choose ONE action from this list:
- search <query> - Search the web for information
- browse <url> - Fetch and read a webpage
- read_file <filename> - Read a file
- list_dir <path> - List files in directory
- run_code <filename> - Run a Python file
- calculate <expression> - Calculate math
- time - Get current time
- llm <question> - Ask LLM for explanation/opinion
- finish <result> - Task is complete, provide final answer

Respond in format:
ACTION: <action_name>
DETAIL: <specific details>
"""
        
        try:
            response = self.call_llm_simple(prompt)
            
            # Parse response
            action_type = "finish"
            detail = ""
            final_response = response
            
            for line in response.split('\n'):
                if line.startswith('ACTION:'):
                    action_type = line.replace('ACTION:', '').strip().lower()
                elif line.startswith('DETAIL:'):
                    detail = line.replace('DETAIL:', '').strip()
                elif line.startswith('RESPONSE:'):
                    final_response = line.replace('RESPONSE:', '').strip()
            
            return {
                'type': action_type,
                'detail': detail,
                'response': final_response
            }
        
        except Exception as e:
            return {'type': 'finish', 'response': f"Error: {str(e)}"}
    
    def execute_action(self, action, original_task):
        """Execute a single action"""
        action_type = action['type']
        detail = action.get('detail', '')
        
        if action_type == 'search':
            return self.web_search(detail or original_task)
        
        elif action_type == 'browse':
            return self.browse_url(detail)
        
        elif action_type == 'read_file':
            return self.read_file(detail)
        
        elif action_type == 'list_dir':
            return self.list_directory(detail or ".")
        
        elif action_type == 'run_code':
            return self.run_code(detail)
        
        elif action_type == 'calculate':
            try:
                expr = self.extract_math(detail or original_task)
                if expr:
                    return f"Result: {eval(expr)}"
            except:
                pass
            return "Could not calculate."
        
        elif action_type == 'time':
            return f"Current time: {time.strftime('%H:%M:%S')}"
        
        elif action_type == 'llm':
            return self.call_llm_simple(detail or original_task)
        
        elif action_type == 'finish':
            return action.get('response', 'Done')
        
        else:
            # Default: use LLM
            return self.call_llm_simple(original_task)
    
    def is_task_done(self, task, result):
        """Check if task seems complete"""
        # Simple heuristics
        result_lower = result.lower()
        
        # If result has substantial content, probably done
        if len(result) > 50:
            # Check for completion indicators
            done_indicators = ['completed', 'done', 'finished', 'result is', 'answer:']
            if any(indicator in result_lower for indicator in done_indicators):
                return True
            
            # If LLM provided a full answer, probably done
            if 'according to' in result_lower or 'here is' in result_lower:
                return True
        
        return False
    
    def finish_task(self, response):
        """Placeholder for finish action"""
        return response
    
    # ============ PLANNING (for non-autonomous mode) ============
    def plan(self, task):
        task_lower = task.lower()
        plan = []
        
        complex_keywords = ["explain", "why", "how does", "write code", "help me", "can you", "what do you think", "describe"]
        
        if any(kw in task_lower for kw in complex_keywords):
            plan.append(("tool", "llm", task))
        
        elif "read" in task_lower and "file" in task_lower:
            match = re.search(r'file\s+([^\s]+)|([^\s]+\.(py|txt|json|md))', task)
            if match:
                plan.append(("tool", "read_file", match.group(1) or match.group(2)))
        
        elif "list" in task_lower and "file" in task_lower:
            plan.append(("tool", "list_dir", "."))
        
        elif "run" in task_lower or ".py" in task:
            match = re.search(r'([^\s]+\.py)', task)
            if match:
                plan.append(("tool", "run_code", match.group(1)))
        
        elif "remember" in task_lower or "my name is" in task_lower:
            plan.append(("store_fact", task))
        
        elif "what did i tell you" in task_lower or "what's my name" in task_lower:
            plan.append(("recall_all_facts", None))
        
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
        
        elif "calculate" in task_lower or any(op in task for op in ["+", "-", "*", "/"]):
            plan.append(("tool", "calculator", task))
        
        elif "time" in task_lower:
            plan.append(("tool", "time", None))
        
        elif "who are you" in task_lower:
            plan.append(("respond", "I am an autonomous AI agent!"))
        
        elif "forget" in task_lower or "clear" in task_lower:
            plan.append(("clear_memory", None))
        
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
                
                if tool_name == "search":
                    param = param.replace("?", "").strip() if param else ""
                    results.append(self.web_search(param))
                
                elif tool_name == "calculator":
                    try:
                        expr = self.extract_math(original_task)
                        if expr:
                            results.append(f"Calculation: {expr} = {eval(expr)}")
                    except:
                        results.append("Error")
                
                elif tool_name == "time":
                    results.append(f"Time: {time.strftime('%H:%M:%S')}")
                
                elif tool_name == "llm":
                    results.append(self.call_llm_simple(param))
                
                elif tool_name == "read_file":
                    results.append(self.read_file(param))
                
                elif tool_name == "run_code":
                    results.append(self.run_code(param))
                
                elif tool_name == "list_dir":
                    results.append(self.list_directory(param))
            
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
        if expr:
            return "".join(expr)
        return None
    
    # ============ TOOLS ============
    def web_search(self, query):
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=3)
            if not results:
                return "No results."
            return "\n".join(f"{r.get('title','')}: {r.get('body','')[:100]}..." for r in results)
        except Exception as e:
            return f"Search error: {e}"
    
    def browse_url(self, url):
        """Fetch and read a webpage"""
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            # Extract text content (simple approach)
            text = response.text
            
            # Remove scripts and styles
            import re
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            
            # Get text between body tags
            body_match = re.search(r'<body[^>]*>(.*?)</body>', text, re.DOTALL)
            if body_match:
                text = body_match.group(1)
            
            # Strip remaining HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text[:2000]
        
        except Exception as e:
            return f"Error browsing {url}: {e}"
    
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
    
    def open_url(self, url):
        return f"Would open: {url}"
    
    def calculate(self, expr):
        try:
            return str(eval(expr))
        except:
            return "Error"
    
    def get_time(self):
        return time.strftime("%H:%M:%S")
    
    # ============ LLM ============
    def call_llm(self, prompt, context=""):
        system_prompt = "You are a helpful AI assistant. Be concise."
        return self.call_llm_simple(prompt, system_prompt)
    
    def call_llm_simple(self, prompt, system_prompt="You are a helpful AI assistant."):
        try:
            if self.llm_provider == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "gemma3:4b",
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
print("Autonomous Agent v8 - Self-Thinking AI!")
print("=" * 60)
print("""
New in v8: AUTONOMOUS MODE!

Type your task and the agent will:
1. Think about what to do
2. Execute actions
3. Observe results
4. Repeat until done

Commands:
- Type normally for single-step mode
- Type 'auto:' followed by task for autonomous mode
- Type 'quit' to exit
""")

agent = AutonomousAgent(llm_provider="ollama")

while True:
    try:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        # Check for autonomous mode
        if user_input.startswith('auto:'):
            task = user_input[5:].strip()
            agent.think(task, autonomous=True)
        else:
            response = agent.think(user_input)
            print(f"\nAgent: {response}")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
