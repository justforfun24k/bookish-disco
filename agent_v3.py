import re
import time
from ddgs import DDGS

class SimpleAgent:
    def __init__(self):
        self.memory = []
        self.tools = {
            "search": self.web_search,
            "calculator": self.calculate,
            "time": self.get_time,
            "open_url": self.open_url,
        }
    
    def think(self, user_input):
        self.memory.append(f"User: {user_input}")
        
        # Show thinking process
        print(f"[Thinking...]")
        
        # Simple chain of thought
        plan = self.plan(user_input)
        
        print(f"[Plan: {len(plan)} step(s)]")
        
        result = self.execute(plan, user_input)
        
        self.memory.append(f"Agent: {result}")
        
        return result
    
    def plan(self, task):
        task = task.lower()
        plan = []
        
        # Multi-step planning
        if "search" in task or "what is" in task or "who is" in task or "tell me about" in task:
            query = task.replace("search", "").replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            if query:
                plan.append(("tool", "search", query))
        
        if "calculate" in task or any(op in task for op in ["+", "-", "*", "/"]):
            plan.append(("tool", "calculator", task))
        
        if "time" in task:
            plan.append(("tool", "time", None))
        
        if "what time" in task and "in" in task:
            # More complex: get time in specific location
            plan.append(("tool", "search", task))
        
        if "who are you" in task:
            plan.append(("respond", "I am a simple AI agent! I can search the web, calculate, tell time, and remember our conversation."))
        
        if "remember" in task:
            plan.append(("recall", None))
        
        if "forget" in task or "clear memory" in task:
            plan.append(("clear_memory", None))
        
        if not plan:
            plan.append(("respond", "I'm not sure how to help with that. Try asking about something, calculating math, or telling time."))
        
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
            
            elif step_type == "recall":
                results.append(f"I remember {len(self.memory)} messages in our conversation.")
            
            elif step_type == "clear_memory":
                count = len(self.memory)
                self.memory = []
                results.append(f"Memory cleared. I forgot {count//2} messages.")
        
        return "\n".join(results) if results else "Done."
    
    def extract_math(self, text):
        expr = re.findall(r'[\d\+\-\*\/\.]+', text)
        if expr:
            return "".join(expr)
        return None
    
    # ============ BETTER SEARCH ============
    def web_search(self, query):
        """Perform search and return clean results"""
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=3)
            
            if not results:
                return "No results found."
            
            # Format nicely
            formatted = []
            for r in results:
                title = r.get('title', 'No title')
                body = r.get('body', '')[:150]  # Limit body length
                
                # Clean up
                if body:
                    formatted.append(f"📌 {title}\n   {body}...")
                else:
                    formatted.append(f"📌 {title}")
            
            return "\n\n".join(formatted)
        
        except Exception as e:
            return f"Search error: {str(e)}"
    
    # ============ TOOL FUNCTIONS ============
    def calculate(self, expr):
        try:
            return str(eval(expr))
        except:
            return "Error"
    
    def get_time(self):
        return time.strftime("%H:%M:%S")
    
    def open_url(self, url):
        """Tool to open a URL (placeholder)"""
        return f"Would open: {url}"
    
    def show_memory(self):
        print("\n--- Memory ---")
        for msg in self.memory[-10:]:
            print(msg)
        print("--------------\n")


# Test the agent
agent = SimpleAgent()

print("=" * 60)
print("AI Agent v3 - Smarter Planning & Better Results!")
print("=" * 60)

test_inputs = [
    "What is Python?",
    "Who is Elon Musk?",
    "Tell me about AI",
    "Calculate 10 * 5 + 3",
    "What time is it?",
    "Remember this: my name is Kai",
    "What did I tell you my name was?",
    "Forget everything",
]

for user_input in test_inputs:
    print(f"\n{'='*40}")
    print(f"User: {user_input}")
    response = agent.think(user_input)
    print(f"\nAgent: {response}")

agent.show_memory()
