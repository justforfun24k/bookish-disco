import re
import time
from ddgs import DDGS

class SmartAgent:
    def __init__(self, llm_api_url=None):
        self.memory = []          # Conversation history
        self.facts = {}           # Key-value facts
        self.llm_api_url = llm_api_url  # For connecting to LLM
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
            "llm": self.call_llm,
        }
    
    def think(self, user_input):
        self.memory.append(f"User: {user_input}")
        
        print(f"[Thinking...]")
        
        # Decide: use LLM or simple planner?
        # For now, use simple planner but add LLM for complex tasks
        plan = self.plan(user_input)
        
        print(f"[Plan: {len(plan)} step(s)]")
        
        result = self.execute(plan, user_input)
        
        self.memory.append(f"Agent: {result}")
        
        return result
    
    def plan(self, task):
        task = task.lower()
        plan = []
        
        # Complex tasks -> use LLM
        complex_keywords = ["explain", "why", "how does", "write code", "help me", "can you"]
        
        if any(kw in task for kw in complex_keywords):
            plan.append(("tool", "llm", task))
        
        # Store facts
        elif "remember" in task or "my name is" in task or "i am" in task:
            plan.append(("store_fact", task))
        
        # Recall facts
        elif "what did i tell you" in task or "what's my name" in task or "my name is" in task:
            plan.append(("recall_all_facts", None))
        
        # What is X? - check facts first, then search
        elif "what is" in task or "who is" in task:
            query = task.replace("what is", "").replace("who is", "").replace("?", "").strip()
            if query in self.facts:
                plan.append(("recall_fact", query))
            else:
                query_clean = task
                for phrase in ["what is", "who is"]:
                    query_clean = query_clean.replace(phrase, "")
                query_clean = query_clean.replace("?", "").strip()
                if query_clean:
                    plan.append(("tool", "search", query_clean))
        
        # Search
        elif "search" in task or "tell me about" in task:
            query = task
            for phrase in ["search", "tell me about"]:
                query = query.replace(phrase, "")
            query = query.replace("?", "").strip()
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
            plan.append(("respond", "I am an AI agent! I can search the web, calculate, tell time, remember facts, and use LLM for complex questions."))
        
        # Clear memory
        elif "forget" in task or "clear" in task:
            plan.append(("clear_memory", None))
        
        else:
            # Default: use LLM for anything complex
            plan.append(("tool", "llm", task))
        
        return plan
    
    def execute(self, plan, original_task):
        results = []
        
        for i, step in enumerate(plan):
            step_type = step[0]
            
            if step_type == "respond":
                return step[1]
            
            # Store facts
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
            
            # Recall fact
            elif step_type == "recall_fact":
                query = step[1]
                if query in self.facts:
                    results.append(f"{query} is {self.facts[query]}")
                else:
                    results.append(f"I don't know what {query} is.")
            
            # Recall all facts
            elif step_type == "recall_all_facts":
                if self.facts:
                    facts_list = [f"{k}: {v}" for k, v in self.facts.items()]
                    results.append("I remember: " + ", ".join(facts_list))
                else:
                    results.append("I don't remember any facts yet.")
            
            elif step_type == "tool":
                tool_name = step[1]
                param = step[2]
                
                if tool_name == "search":
                    param = param.replace("?", "").replace(".", "").strip()
                    print(f"  → Step {i+1}: Searching for '{param}'...")
                    results.append(self.web_search(param))
                
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
                
                elif tool_name == "llm":
                    print(f"  → Step {i+1}: Using LLM...")
                    # LLM call placeholder - would connect to GPT/Claude/Ollama
                    results.append("[LLM response would go here - need to configure API]")
            
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
    
    # ============ LLM (placeholder) ============
    def call_llm(self, prompt):
        """Connect to LLM API - would use Ollama, OpenAI, Claude, etc."""
        # This is a placeholder
        # Real implementation would use requests to call LLM API
        return "[LLM would respond here]"
    
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
agent = SmartAgent()

print("=" * 60)
print("Smart Agent v5 - With LLM Planning!")
print("=" * 60)
print("\nNote: LLM integration needs API configuration (Ollama/OpenAI)")
print()

test_inputs = [
    "What is Python?",
    "My name is Kai",
    "What's my name?",
    "Calculate 100 * 5 + 25",
    "What time is it?",
    "Tell me about quantum computing",
    "How does a neural network work?",
]

for user_input in test_inputs:
    print(f"\n{'='*50}")
    print(f"User: {user_input}")
    response = agent.think(user_input)
    print(f"\nAgent: {response}")

agent.show_memory()
