"""
multi_agent_v2.py - Multi-Agent System with Specialists
Step 2: Main planner agent delegates to specialist agents

Main Agent (Planner) → Specialist Agents:
  - Researcher (searches web)
  - Coder (writes/runs code)
  - Writer (creates content)
  - Calculator (does math)
"""
import sys
sys.path.insert(0, "D:\\books\\src\\py\\ai_agent")

from agent_v9 import Agent


class Specialist:
    """A specialist agent with a specific role"""
    
    def __init__(self, name, role, system_prompt):
        self.name = name
        self.role = role
        self.agent = Agent(name=name)
        self.agent.system_prompt = system_prompt
    
    def run(self, task):
        """Run task with specialist's expertise"""
        return self.agent.think(task)


class MultiAgentSystem:
    """Main agent with specialist agents"""
    
    def __init__(self):
        # Main planner agent
        self.planner = Agent(name="Main", model="tinyllama:latest")
        
        # Create specialists
        self.specialists = {
            "researcher": Specialist(
                "Researcher",
                "search",
                "You are a research expert. Find accurate information from web searches."
            ),
            "coder": Specialist(
                "Coder",
                "code",
                "You are a Python coding expert. Write clean, working code."
            ),
            "writer": Specialist(
                "Writer",
                "write",
                "You are a creative writer. Write engaging content."
            ),
            "calculator": Specialist(
                "Calculator",
                "math",
                "You are a math expert. Solve calculations accurately."
            ),
        }
    
    def delegate(self, task):
        """Main agent delegates task to appropriate specialist"""
        # First, ask main agent to analyze the task
        analysis = self.planner.think(f"Analyze this task and decide which specialist should handle it: {task}")
        
        # Determine which specialist to use
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["search", "find", "what is", "who is", "research"]):
            specialist = self.specialists["researcher"]
        elif any(word in task_lower for word in ["code", "python", "write", "program", "implement"]):
            specialist = self.specialists["coder"]
        elif any(word in task_lower for word in ["write", "essay", "story", "article", "create content"]):
            specialist = self.specialists["writer"]
        elif any(word in task_lower for word in ["calculate", "math", "+", "-", "*", "/", "="]):
            specialist = self.specialists["calculator"]
        else:
            # Default to main agent
            return self.planner.think(task)
        
        # Run with specialist
        result = specialist.run(task)
        
        return f"[{specialist.name}] {result}"
    
    def chat(self, user_input):
        """Chat with main agent or delegate to specialist"""
        if user_input.startswith("delegate "):
            task = user_input[9:]
            return self.delegate(task)
        elif user_input.startswith("ask "):
            specialist_name = user_input.split()[1]
            task = " ".join(user_input.split()[2:])
            if specialist_name in self.specialists:
                return self.specialists[specialist_name].run(task)
            return f"Unknown specialist: {specialist_name}"
        elif user_input == "list":
            return "Specialists: " + ", ".join(self.specialists.keys())
        else:
            return self.planner.think(user_input)


# ==================== MAIN ====================
if __name__ == "__main__":
    system = MultiAgentSystem()
    
    print("=" * 50)
    print("Multi-Agent System v2 - With Specialists")
    print("=" * 50)
    print("Commands:")
    print("  - Type normally to chat with main agent")
    print("  - 'delegate <task>' - delegate to specialist")
    print("  - 'ask researcher <question>' - ask specific specialist")
    print("  - 'ask coder <question>'")
    print("  - 'ask writer <question>'")
    print("  - 'list' - show all specialists")
    print("  - 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            result = system.chat(user_input)
            print(f"\n{result}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
