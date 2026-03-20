import re
import time
import urllib.request
import urllib.parse
import json

class SimpleAgent:
    def __init__(self):
        self.memory = []  # Store conversation history
        self.tools = {
            "search": self.web_search,  # Now real search!
            "calculator": self.calculate,
            "time": self.get_time,
        }
    
    def think(self, user_input):
        """Main agent loop"""
        # 1. Remember user input
        self.memory.append(f"User: {user_input}")
        
        # 2. Plan what to do
        plan = self.plan(user_input)
        
        # 3. Execute plan
        result = self.execute(plan, user_input)
        
        # 4. Remember agent response
        self.memory.append(f"Agent: {result}")
        
        return result
    
    def plan(self, task):
        """Break task into steps"""
        task = task.lower()
        
        # Simple keyword matching
        plan = []
        
        if "search" in task or "what is" in task or "who is" in task or "tell me about" in task:
            # Extract search query
            query = task.replace("search", "").replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            if query:
                plan.append(("tool", "search", query))
        
        if "calculate" in task or any(op in task for op in ["+", "-", "*", "/"]):
            plan.append(("tool", "calculator", task))
        
        if "time" in task:
            plan.append(("tool", "time", None))
        
        if "who are you" in task:
            plan.append(("respond", "I am a simple AI agent!"))
        
        if "remember" in task:
            plan.append(("recall", None))
        
        if not plan:
            plan.append(("respond", "I'm not sure how to help with that."))
        
        return plan
    
    def execute(self, plan, original_task):
        """Execute each step in plan"""
        results = []
        
        for step in plan:
            step_type = step[0]
            
            if step_type == "respond":
                return step[1]  # Return directly
            
            elif step_type == "tool":
                tool_name = step[1]
                param = step[2]
                
                if tool_name == "search":
                    print(f"[Searching for: '{param}'...]")
                    search_results = self.web_search(param)
                    results.append(search_results)
                
                elif tool_name == "calculator":
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
                results.append(f"I remember: {len(self.memory)} messages")
        
        return "\n".join(results) if results else "Done."
    
    def extract_math(self, text):
        """Extract math expression from text"""
        expr = re.findall(r'[\d\+\-\*\/\.]+', text)
        if expr:
            return "".join(expr)
        return None
    
    # ============ REAL WEB SEARCH ============
    def web_search(self, query):
        """Perform real web search using DuckDuckGo API"""
        try:
            # Use DuckDuckGo instant answer API (free, no API key needed)
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Get the answer
            if data.get('AbstractText'):
                return data['AbstractText'][:500]  # First 500 chars
            
            # If no direct answer, get related topics
            related = data.get('RelatedTopics', [])
            if related:
                results = []
                for item in related[:3]:  # Top 3 results
                    if 'Text' in item:
                        results.append(item['Text'][:200])
                if results:
                    return "Related results:\n" + "\n".join(f"- {r}" for r in results)
            
            return "No results found."
        
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
    
    def show_memory(self):
        """Show conversation history"""
        print("\n--- Memory ---")
        for msg in self.memory[-10:]:
            print(msg)
        print("--------------\n")


# Test the agent
agent = SimpleAgent()

print("=" * 50)
print("Testing AI Agent v2 - With Real Web Search!")
print("=" * 50)

test_inputs = [
    "What is Python?",
    "Who is Elon Musk?",
    "Tell me about AI",
    "Calculate 10 * 5 + 3",
]

for user_input in test_inputs:
    print(f"\nUser: {user_input}")
    response = agent.think(user_input)
    print(f"Agent: {response}")

agent.show_memory()
