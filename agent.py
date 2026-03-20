import re
import time

class SimpleAgent:
    def __init__(self):
        self.memory = []  # Store conversation history
        self.tools = {
            "search": self.search,
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
        
        if "weather" in task:
            plan.append(("tool", "search", "weather"))
        
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
                    # Simulate search
                    results.append(f"[Search results for '{param}']")
                    results.append("Result 1: Example search result")
                    results.append("Result 2: Another example")
                
                elif tool_name == "calculator":
                    try:
                        # Extract and evaluate math
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
        # Find numbers and operators
        expr = re.findall(r'[\d\+\-\*\/\.]+', text)
        if expr:
            return "".join(expr)
        return None
    
    # Tool functions
    def search(self, query):
        return f"Results for: {query}"
    
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
        for msg in self.memory[-10:]:  # Last 10 messages
            print(msg)
        print("--------------\n")


# Test the agent
agent = SimpleAgent()

# Test examples
print("=" * 50)
print("Testing AI Agent")
print("=" * 50)

test_inputs = [
    "Hello! Who are you?",
    "What's the weather today?",
    "Calculate 5 + 3 * 2",
    "What time is it?",
    "Do you remember anything?",
]

for user_input in test_inputs:
    print(f"\nUser: {user_input}")
    response = agent.think(user_input)
    print(f"Agent: {response}")

# Show memory
agent.show_memory()
