import re
import time
from ddgs import DDGS

class SimpleAgent:
    def __init__(self):
        self.memory = []          # Conversation history
        self.facts = {}           # Key-value facts
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
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
        task = task.lower()
        plan = []
        
        # Store facts: "remember X is Y" or "my name is X"
        if "remember" in task or "my name is" in task or "i am" in task:
            plan.append(("store_fact", task))
        
        # Recall facts: "what is X" or "what did i tell you"
        elif "what is" in task and "my" not in task:
            query = task.replace("what is", "").replace("?", "").strip()
            plan.append(("recall_fact", query))
        
        elif "what did i tell you" in task or "what's my name" in task or "my name is" in task:
            plan.append(("recall_all_facts", None))
        
        # Search
        elif "search" in task or "what is" in task or "who is" in task or "tell me about" in task:
            query = task
            for phrase in ["search", "what is", "who is", "tell me about"]:
                query = query.replace(phrase, "")
            query = query.replace("?", "").replace(".", "").strip()
            if query:
                plan.append(("tool", "search", query))
        
        # Calculate
        elif "calculate" in task or any(op in task for op in ["+", "-", "*", "/"]):
            plan.append(("tool", "calculator", task))
        
        # Time
        elif "time" in task:
            plan.append(("tool", "time", None))
        
        # Who are you
        elif "who are you" in task:
            plan.append(("respond", "I am a simple AI agent! I can search the web, calculate, tell time, and remember facts you tell me."))
        
        # Clear memory
        elif "forget" in task or "clear" in task:
            plan.append(("clear_memory", None))
        
        else:
            plan.append(("respond", "I'm not sure how to help with that. Try asking about something, calculating math, or telling me something to remember."))
        
        return plan
    
    def execute(self, plan, original_task):
        results = []
        
        for i, step in enumerate(plan):
            step_type = step[0]
            
            if step_type == "respond":
                return step[1]
            
            # Store facts from user input
            elif step_type == "store_fact":
                print(f"  → Step {i+1}: Storing fact...")
                # Extract: "my name is Kai" -> name: Kai
                task = original_task.lower()
                
                if "my name is" in task:
                    name = original_task.lower().replace("my name is", "").strip()
                    self.facts["name"] = name.title()
                    results.append(f"Okay! I'll remember your name is {self.facts['name']}")
                
                elif "remember" in task:
                    # Try to extract: "remember X is Y"
                    match = re.search(r'remember (.*?) is (.*)', task)
                    if match:
                        key = match.group(1).strip()
                        value = match.group(2).strip()
                        self.facts[key] = value
                        results.append(f"Okay! I'll remember that {key} is {value}")
                    else:
                        results.append("I didn't understand what to remember. Try 'my name is [name]' or 'remember [key] is [value]'.")
                
                else:
                    results.append("I didn't understand. Try 'my name is [name]'.")
            
            # Recall a specific fact
            elif step_type == "recall_fact":
                query = step[1]
                print(f"  → Step {i+1}: Recalling '{query}'...")
                if query in self.facts:
                    results.append(f"{query} is {self.facts[query]}")
                else:
                    results.append(f"I don't know what {query} is. Tell me!")
            
            # Recall all facts
            elif step_type == "recall_all_facts":
                print(f"  → Step {i+1}: Recalling all facts...")
                if self.facts:
                    facts_list = [f"{k}: {v}" for k, v in self.facts.items()]
                    results.append("I remember: " + ", ".join(facts_list))
                else:
                    results.append("I don't remember any facts yet. Tell me something!")
            
            elif step_type == "tool":
                tool_name = step[1]
                param = step[2]
                
                if tool_name == "search":
                    # Clean query - remove punctuation
                    param = param.replace("?", "").replace(".", "").replace("!", "").strip()
                    print(f"  → Step {i+1}: Searching for '{param}'...")
                    search_results = self.web_search(param)
                    results.append(search_results)
                
                elif tool_name == "calculator":
                    print(f"  → Step {i+1}: Calculating...")
                    try:
                        expr = self.extract_math(original_task)
                        if expr:
                            answer = eval(expr)
                            results.append(f"Calculation: {expr} = {answer}")
                    except:
                        results.append("Could not calculate that.")
                
                elif tool_name == "time":
                    results.append(f"Current time: {time.strftime('%H:%M:%S')}")
            
            elif step_type == "clear_memory":
                mem_count = len(self.memory)
                fact_count = len(self.facts)
                self.memory = []
                self.facts = {}
                results.append(f"Memory cleared! I forgot {mem_count//2} messages and {fact_count} facts.")
        
        return "\n".join(results) if results else "Done."
    
    def extract_math(self, text):
        expr = re.findall(r'[\d\+\-\*\/\.]+', text)
        if expr:
            return "".join(expr)
        return None
    
    # ============ SEARCH ============
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
    
    # ============ TOOLS ============
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


# Test
agent = SimpleAgent()

print("=" * 60)
print("AI Agent v4 - Fact Memory!")
print("=" * 60)

test_inputs = [
    "What is Python?",
    "Who is Elon Musk?",
    "My name is Kai",
    "What's my name?",
    "Remember Python is a programming language",
    "What is Python?",
    "What did I tell you?",
    "Calculate 100 / 5 + 10",
    "What time is it?",
    "Forget everything",
]

for user_input in test_inputs:
    print(f"\n{'='*40}")
    print(f"User: {user_input}")
    response = agent.think(user_input)
    print(f"\nAgent: {response}")

agent.show_memory()
