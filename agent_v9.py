"""
agent_v9.py - Simple Agent Architecture
Perceive -> Plan -> Act

A cleaner, more understandable agent design.
"""
import re
import time
import os
import subprocess
import requests
import sys
from collections import deque
from ddgs import DDGS


class Agent:
    """Simple Agent with Perceive -> Plan -> Act architecture"""
    
    def __init__(self, name="Agent", memory_size=6, llm_provider="ollama",model="tinyllama:latest"):
        self.name = name
        self.memory = deque(maxlen=memory_size)  # Short-term memory
        self.facts = {}  # Long-term facts
        self.browse_cache = {}
        self.browse_history = []
        self.llm_provider = llm_provider
        
        # Available tools
        self.tools = {
            "search": self.tool_search,
            "browse": self.tool_browse,
            "time": self.tool_time,
            "llm": self.tool_llm,
            "read_file": self.tool_read_file,
            "list_dir": self.tool_list_dir,
            "run_code": self.tool_run_code,
            "write_file": self.tool_write_file,
            "shell": self.tool_shell,
            "dictionary": self.tool_dictionary,
            "show_model": self.tool_show_model,
            "clear_session": self.tool_clear_session,
            "execute_python": self.tool_execute_python,
            "save_session": self.tool_save_session,
            "load_session": self.tool_load_session,
            "todo": self.tool_todo,
            "weather": self.tool_weather,
        }
        
        # Todo list
        self.todos = []
        
        # Current model name (settable)
        self.model = "gemma3:4b"
        
        # Weather API key
        self.weather_api_key = "7e40416d255108ccc6196f353568857f"
    
    # ==================== PERSISTENCE ====================
    def save(self, filepath=None):
        """Save agent state to file"""
        if filepath is None:
            filepath = f"{self.name}_session.json"
        
        import json
        data = {
            "name": self.name,
            "memory": list(self.memory),
            "facts": self.facts,
            "browse_cache": {k: v[:500] for k, v in self.browse_cache.items()},  # Truncate long content
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return f"Saved to {filepath}"
    
    def load(self, filepath):
        """Load agent state from file"""
        import json
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.name = data.get("name", self.name)
            from collections import deque
            self.memory = deque(data.get("memory", []), maxlen=6)
            self.facts = data.get("facts", {})
            self.browse_cache = {}
            
            return f"Loaded from {filepath}"
        except FileNotFoundError:
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error loading: {e}"
    
    # ==================== PERCEIVE ====================
    def perceive(self, user_input):
        """Get input and prepare context"""
        # Store in memory
        self.memory.append(f"User: {user_input}")
        
        # Build context from memory
        context = "\n".join(list(self.memory))
        
        return {
            "input": user_input,
            "context": context,
            "facts": self.facts
        }
    
    # ==================== PLAN ====================
    def plan(self, perception):
        """Decide what action to take"""
        user_input = perception["input"]
        context = perception["context"]
        
        # Simple keyword-based planning
        task = user_input.lower()
        
        # Check for fact questions first
        if "what is" in task or "who is" in task:
            query = task.replace("what is", "").replace("who is", "").strip()
            if query in perception["facts"]:
                return {"tool": "respond", "content": f"{query} is {perception['facts'][query]}"}
        
        # Check for remember/forget
        if "remember" in task or "my name is" in task:
            return {"tool": "store_fact", "content": user_input}
        
        if "what did i tell" in task or "what's my name" in task:
            if self.facts:
                facts_str = ", ".join(f"{k}: {v}" for k, v in self.facts.items())
                return {"tool": "respond", "content": f"I remember: {facts_str}"}
            return {"tool": "respond", "content": "I don't remember any facts."}
        
        if "forget" in task or "clear" in task:
            return {"tool": "clear_memory", "content": ""}
        
        # Use LLM for complex tasks
        complex_keywords = ["explain", "why", "how does", "tell me about", "what do you think"]
        if any(kw in task for kw in complex_keywords):
            return {"tool": "llm", "content": user_input}
        
        # Search
        if "search" in task or "what is" in task or "who is" in task:
            query = task
            for phrase in ["search", "what is", "who is"]:
                query = query.replace(phrase, "")
            query = query.replace("?", "").strip()
            if query:
                return {"tool": "search", "content": query}
        
        # Browse
        if "browse" in task or "open" in task:
            match = re.search(r'(https?://[^\s]+)|([a-z]+\.[a-z]+)', user_input)
            if match:
                url = match.group(1) or match.group(2)
                return {"tool": "browse", "content": url}
        
        # Time
        if "time" in task:
            return {"tool": "time", "content": ""}
        
        # Read file
        if "read" in task and "file" in task:
            match = re.search(r'file\s+(\S+)|(\S+\.(py|txt|md))', user_input)
            if match:
                filename = match.group(1) or match.group(2)
                return {"tool": "read_file", "content": filename}
        
        # List files
        if "list" in task and "file" in task:
            return {"tool": "list_dir", "content": "."}
        
        # Run code
        if ".py" in user_input:
            match = re.search(r'(\S+\.py)', user_input)
            if match:
                return {"tool": "run_code", "content": match.group(1)}
        
        # Write file
        if "write" in task and "file" in task:
            match = re.search(r'file\s+(\S+)|(\S+\.(py|txt|md))', user_input)
            if match:
                filename = match.group(1) or match.group(2)
                content = user_input
                return {"tool": "write_file", "content": f"{filename}|{content}"}
        
        # Shell command
        if "run" in task and ("command" in task or "shell" in task):
            cmd = user_input
            for word in ["run", "command", "shell", "execute"]:
                cmd = cmd.replace(word, "")
            cmd = cmd.strip()
            if cmd:
                return {"tool": "shell", "content": cmd}
        
        # Dictionary
        if "define" in task or "meaning of" in task or "what does" in task:
            query = task
            for phrase in ["define", "meaning of", "what does", "what is the meaning of"]:
                query = query.replace(phrase, "")
            query = query.replace("?", "").strip()
            if query:
                return {"tool": "dictionary", "content": query}
        
        # Execute Python code
        if "run python" in task or "execute python" in task or "eval" in task:
            code = user_input
            for phrase in ["run python", "execute python", "eval", "python"]:
                code = code.replace(phrase, "")
            code = code.strip()
            if code:
                return {"tool": "execute_python", "content": code}
        
        # Save session
        if "save" in task and ("session" in task or "memory" in task):
            match = re.search(r'save.*?(to\s+)?(\S+\.json)', user_input, re.IGNORECASE)
            filepath = match.group(2) if match else ""
            return {"tool": "save_session", "content": filepath}
        
        # Load session
        if "load" in task and ("session" in task or "memory" in task):
            match = re.search(r'load.*?(from\s+)?(\S+\.json)', user_input, re.IGNORECASE)
            filepath = match.group(2) if match else ""
            return {"tool": "load_session", "content": filepath}
        
        # Todo
        if "todo" in task or "task" in task:
            action = user_input
            for phrase in ["todo", "task"]:
                action = action.replace(phrase, "")
            action = action.strip()
            return {"tool": "todo", "content": action if action else "list"}
        
        # Weather
        if "weather" in task:
            city = task.replace("weather", "").replace("in", "").replace("?", "").strip()
            if city:
                return {"tool": "weather", "content": city}
            return {"tool": "weather", "content": "London"}
        
        # Show model
        if "show" in task and "model" in task:
            return {"tool": "show_model", "content": ""}
        
        # Clear session
        if "clear" in task and ("session" in task or "chat" in task or "conversation" in task):
            return {"tool": "clear_session", "content": ""}
        
        # Who are you
        if "who are you" in task:
            return {"tool": "respond", "content": f"I am {self.name}, an AI agent! I can search, browse, run Python, read files, weather, todo, and chat."}
        
        #if "calculate" in task or any(op in task for op in ["+", "-", "*", "/"]):
         #   return {"tool": "calculator", "content": ""}
        # Default: use LLM
        return {"tool": "llm", "content": user_input}
    
    # ==================== ACT ====================
    def act(self, plan):
        """Execute the planned action"""
        tool_name = plan["tool"]
        content = plan["content"]
        
        if tool_name == "respond":
            return content
        elif tool_name=="calculator":
            return f"no calculate tool."
        elif tool_name == "store_fact":
            task = content.lower()
            if "my name is" in task:
                name = task.replace("my name is", "").strip()
                self.facts["name"] = name.title()
                return f"Okay! I remember your name is {name}"
            elif "remember" in task:
                match = re.search(r'remember (.*?) is (.*)', task)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    self.facts[key] = value
                    return f"Remembered: {key} is {value}"
            return "I didn't understand what to remember."
        
        elif tool_name == "clear_memory":
            self.memory.clear()
            self.facts = {}
            return "Memory cleared!"
        
        # Call appropriate tool
        if tool_name in self.tools:
            return self.tools[tool_name](content)
        
        return f"Unknown tool: {tool_name}"
    
    # ==================== MAIN LOOP ====================
    def think(self, user_input):
        """Complete Perceive -> Plan -> Act cycle"""
        # 1. Perceive
        perception = self.perceive(user_input)
        
        # 2. Plan
        plan = self.plan(perception)
        
        # 3. Act
        response = self.act(plan)
        
        # Store response in memory
        self.memory.append(f"Agent: {response}")
        
        return response
    
    # ==================== TOOLS ====================
    def tool_search(self, query):
        """Search the web"""
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=3)
            if not results:
                return "No results found."
            return "\n".join(f"- {r.get('title','')}: {r.get('body','')[:100]}..." for r in results)
        except Exception as e:
            return f"Search error: {e}"
    
    def tool_browse(self, url):
        """Browse a URL and get summary"""
        # Check cache
        if url in self.browse_cache:
            return self.browse_cache[url]
        
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            html = response.text
            
            # Extract title
            m_title = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
            title = m_title.group(1).strip() if m_title else url
            
            # Extract first paragraph
            m_para = re.search(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE|re.DOTALL)
            summary = ""
            if m_para:
                para = re.sub(r'<[^>]+>', '', m_para.group(1))
                summary = para.strip()
            if not summary:
                text = re.sub(r'<[^>]+>', ' ', html)
                summary = ' '.join(text.split()[:60])
            
            summary = re.sub(r'\s+', ' ', summary).strip()
            
            result = f"Title: {title}\nSummary: {summary}...\nURL: {url}"
            self.browse_cache[url] = result
            self.browse_history.append((url, title, summary))
            return result
        except Exception as e:
            return f"Error browsing {url}: {e}"
    
    def tool_time(self, _):
        """Get current time"""
        return f"Current time: {time.strftime('%H:%M:%S')}"
    
    def tool_llm(self, prompt):
        """Ask the LLM"""
        system_prompt = "You are a helpful AI assistant. Be concise and friendly."
        
        try:
            if self.llm_provider == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                    },
                    timeout=100
                )
                if response.status_code == 200:
                    return response.json()["message"]["content"]
                else:
                    return f"[Error: {response.status_code}]"
        except Exception as e:
            return f"[Error: {e}]"
    
    def tool_read_file(self, filepath):
        """Read a file"""
        try:
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()[:2000]
        except FileNotFoundError:
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error: {e}"
    
    def tool_list_dir(self, path="."):
        """List directory contents"""
        try:
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            files = os.listdir(path)
            return ", ".join(files[:20])
        except Exception as e:
            return f"Error: {e}"
    
    def tool_run_code(self, filepath):
        """Run a Python file"""
        try:
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.getcwd(), filepath)
            result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=30)
            return result.stdout or result.stderr
        except Exception as e:
            return f"Error: {e}"
    
    def tool_write_file(self, data):
        """Write content to a file"""
        try:
            parts = data.split("|", 1)
            if len(parts) < 2:
                return "Error: Need filename and content. Format: filename|content"
            
            filename = parts[0].strip()
            content = parts[1].strip()
            
            # Extract content after common phrases
            for phrase in ["write to", "content:", "text:"]:
                if phrase in content.lower():
                    content = content.lower().split(phrase, 1)[1].strip()
            
            if not os.path.isabs(filename):
                filename = os.path.join(os.getcwd(), filename)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Written to {filename}"
        except Exception as e:
            return f"Error: {e}"
    
    def tool_shell(self, command):
        """Run a shell command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout or result.stderr
            return output if output else "(no output)"
        except Exception as e:
            return f"Error: {e}"
    
    def tool_dictionary(self, word):
        """Look up word definition"""
        try:
            ddgs = DDGS()
            results = ddgs.text(f"define {word}", max_results=3)
            if results:
                return results[0].get('body', 'No definition found.')
            return "No definition found."
        except Exception as e:
            return f"Error: {e}"
    
    def tool_show_model(self, _):
        """Show current Ollama model"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    model_names = [m.get("name", "unknown") for m in models]
                    return f"Available models: {', '.join(model_names)}\nCurrent: {self.model}"
                return "No models found."
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def tool_clear_session(self, _):
        """Clear Ollama session state by ending current session"""
        try:
            requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "system", "content": "clear"}],
                    "stream": False,
                },
                timeout=10
            )
            return "Session cleared. Start fresh conversation."
        except Exception as e:
            return f"Error: {e}"
    
    def tool_execute_python(self, code):
        """Execute Python code in memory"""
        try:
            import io
            import contextlib
            
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    exec(code, {"__builtins__": __builtins__}, {})
                result = output.getvalue()
                return result if result else "(no output)"
            except Exception as e:
                return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {e}"
    
    def tool_save_session(self, filepath):
        """Save agent session to file"""
        if not filepath:
            filepath = f"{self.name}_session.json"
        return self.save(filepath)
    
    def tool_load_session(self, filepath):
        """Load agent session from file"""
        return self.load(filepath)
    
    def tool_todo(self, action):
        """Manage todo list: add <task>, list, done <n>, clear"""
        action = action.strip().lower()
        
        if action.startswith("add "):
            task = action[4:].strip()
            self.todos.append({"task": task, "done": False})
            return f"Added: {task}"
        
        if action == "list":
            if not self.todos:
                return "No todos."
            result = []
            for i, t in enumerate(self.todos, 1):
                status = "✓" if t["done"] else " "
                result.append(f"{i}. [{status}] {t['task']}")
            return "\n".join(result)
        
        if action.startswith("done "):
            try:
                idx = int(action.split()[1]) - 1
                if 0 <= idx < len(self.todos):
                    self.todos[idx]["done"] = True
                    return f"Completed: {self.todos[idx]['task']}"
                return "Invalid task number."
            except:
                return "Usage: todo done <number>"
        
        if action == "clear":
            self.todos = []
            return "Todos cleared."
        
        return "Usage: todo add <task> | todo list | todo done <n> | todo clear"
    
    def tool_weather(self, city):
        """Get weather for a city"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=100)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                return f"Weather in {city}: {temp}°C, {desc}, Humidity: {humidity}%"
            elif response.status_code == 401:
                return "Weather API: Invalid API key."
            else:
                return f"Weather API error: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    # ==================== AUTONOMOUS MODE ====================
    def autonomous_loop(self, task, max_iterations=5):
        """Loop: perceive -> plan -> act until done"""
        print(f"\n{'='*50}")
        print(f"AUTONOMOUS MODE: {task}")
        print(f"{'='*50}\n")
        
        context = f"Task: {task}\n"
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"[Iteration {iteration}/{max_iterations}]")
            
            # Perceive
            perception = self.perceive(task)
            perception["context"] = context
            
            # Plan
            plan = self.plan(perception)
            print(f"  → Plan: {plan['tool']}")
            
            # Act
            result = self.act(plan)
            print(f"  → Result: {result[:100]}...")
            
            # Observe
            context += f"Step {iteration}: {result[:200]}\n"
            
            # Check if done
            if self.is_complete(result):
                print(f"\n[Task complete!]")
                break
        
        if iteration >= max_iterations:
            result = f"Max iterations reached. Last result: {result}"
        
        self.memory.append(f"Agent: {result}")
        return result
    
    def is_complete(self, result):
        """Check if task seems complete"""
        if not result:
            return False
        
        result_lower = result.lower()
        
        if "result:" in result_lower and len(result) < 30:
            return True
        
        if len(result) < 15:
            return True
        
        conclusion_phrases = [
            "in conclusion", "in summary", "to summarize",
            "overall", "finally", "in short",
            "that's", "there you have", "thank you"
        ]
        
        if any(phrase in result_lower for phrase in conclusion_phrases):
            return True
        
        if len(result) > 200 and result.count('.') > 3:
            return True
        
        return False


# ==================== MAIN ====================
if __name__ == "__main__":
    agent = Agent(name="KaiAgent", llm_provider="ollama")
    
    print("=" * 50)
    print("Agent v9 - Perceive -> Plan -> Act")
    print("=" * 50)
    print("Commands:")
    print("  - Type normally for single step")
    print("  - Type 'auto:' for autonomous mode")
    print("  - Type '<<<' then lines then 'end' for multi-line")
    print("  - Type 'quit' to exit\n")
    
    def get_input(prompt="You: "):
        """Get input - type <<< to start multi-line, end to finish"""
        line = input(prompt)
        if line.strip().lower() in ['quit', 'exit', 'bye']:
            return line
        
        # Check for multi-line start
        if line.strip() == "<<<":
            lines = []
            while True:
                l = input("... ")
                if l.strip() == "end":
                    break
                lines.append(l)
            return "\n".join(lines)
        
        return line
    
    while True:
        try:
            user_input = get_input()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            # Check for autonomous mode
            if user_input.startswith("auto:"):
                task = user_input[5:].strip()
                result = agent.autonomous_loop(task)
                print(f"\nFinal: {result}\n")
            else:
                result = agent.think(user_input)
                print(f"\nAgent: {result}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break