"""
multi_agent.py - Simple Multi-Agent System
Two agents that can chat with each other

Step 1: Simpler version - Agent A and Agent B can talk to each other
"""
import sys
sys.path.insert(0, "D:\\books\\src\\py\\ai_agent")

from agent_v9 import Agent


class MultiAgent:
    """Two agents that can collaborate"""
    
    def __init__(self):
        # Create two agents with different roles
        self.agent_a = Agent(name="Alice")
        self.agent_b = Agent(name="Bob")
        
        # Set their personalities
        self.agent_a.system_prompt = "You are Alice, a helpful and curious AI assistant."
        self.agent_b.system_prompt = "You are Bob, a friendly and knowledgeable AI assistant."
        
        self.current_agent = self.agent_a
    
    def chat(self, user_input):
        """User chats with current agent"""
        return self.current_agent.think(user_input)
    
    def switch_agent(self):
        """Switch to the other agent"""
        self.current_agent = self.agent_b if self.current_agent == self.agent_a else self.agent_a
        return f"Switched to {self.current_agent.name}"
    
    def ask_other_agent(self, message):
        """Current agent asks the other agent for help"""
        other = self.agent_b if self.current_agent == self.agent_a else self.agent_a
        return other.think(message)
    
    def collaborate(self, task):
        """Both agents work together on a task"""
        # Agent A starts
        response_a = self.agent_a.think(f"Start working on: {task}")
        
        # Ask Agent B for help
        response_b = self.agent_b.think(f"Help with this: {task}. Previous work: {response_a[:100]}")
        
        return f"Alice: {response_a[:100]}...\n\nBob: {response_b[:100]}..."


# ==================== MAIN ====================
if __name__ == "__main__":
    multi = MultiAgent()
    
    print("=" * 50)
    print("Multi-Agent System - Two Agents Chatting")
    print("=" * 50)
    print("Commands:")
    print("  - Type normally to chat with current agent")
    print("  - 'switch' to switch between Alice and Bob")
    print("  - 'ask' to ask the other agent (e.g., 'ask what is Python?')")
    print("  - 'both' to have both agents work together")
    print("  - 'quit' to exit\n")
    
    while True:
        try:
            user_input = input(f"{multi.current_agent.name}> ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'switch':
                print(multi.switch_agent())
                continue
            
            if user_input.lower().startswith('ask '):
                message = user_input[4:]
                result = multi.ask_other_agent(message)
                other_name = multi.agent_b.name if multi.current_agent == multi.agent_a else multi.agent_a.name
                print(f"\n{other_name}: {result}\n")
                continue
            
            if user_input.lower() == 'both':
                task = input("Task: ")
                result = multi.collaborate(task)
                print(f"\n{result}\n")
                continue
            
            result = multi.chat(user_input)
            print(f"\n{multi.current_agent.name}: {result}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
