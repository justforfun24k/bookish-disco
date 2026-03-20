"""
langchain_step4.py - LangChain Step by Step
Step 4: LCEL - LangChain Expression Language

LCEL is the way to compose chains in LangChain:
- | (pipe) - pass output to next step
- .invoke() - run the chain
- .stream() - stream output token by token
- RunnableSequence - the chain object itself
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# =============================================
# Connect to Ollama
# =============================================
llm = ChatOllama(model="tinyllama:latest", temperature=0.3)

# =============================================
# STEP 1: Simple Chain (review)
# =============================================
print("=" * 50)
print("STEP 1: Simple Chain Review")
print("=" * 50)

template = "Explain {topic} in one sentence."
prompt = PromptTemplate.from_template(template)

# Chain = prompt | llm
chain = prompt | llm

response = chain.invoke({"topic": "recursion"})
print(f"Topic: recursion")
print(f"Response: {response.content}")


# =============================================
# STEP 2: Chain with Parser
# =============================================
print("\n" + "=" * 50)
print("STEP 2: Chain with Parser")
print("=" * 50)

# Full chain: prompt | llm | parser
template = """List {count} {item_type}.
Return JSON with "items" key containing the list."""

prompt = PromptTemplate.from_template(template)
parser = JsonOutputParser()

# Chain: input -> prompt -> llm -> parser -> output
chain = prompt | llm | parser

response = chain.invoke({
    "count": 3,
    "item_type": "fruits"
})

print(f"Type: {type(response)}")
print(f"Response: {response}")
print(f"Items: {response.get('items', [])}")


# =============================================
# STEP 3: Runnable Interface
# =============================================
print("\n" + "=" * 50)
print("STEP 3: Runnable Interface")
print("=" * 50)

# Everything in LCEL is a "Runnable"
# You can use these methods:

# .invoke() - synchronous call
result = chain.invoke({"count": 2, "item_type": "colors"})
print(f".invoke(): {result}")

# .batch() - multiple inputs at once
results = chain.batch([
    {"count": 2, "item_type": "animals"},
    {"count": 2, "item_type": "cars"},
])
print(f".batch(): {results}")

# .stream() - streaming output (like real-time)
print(f".stream(): ", end="")
for chunk in chain.stream({"count": 1, "item_type": "color"}):
    print(chunk, end="", flush=True)
print()


# =============================================
# STEP 4: Add Memory (Conversation History)
# =============================================
print("\n" + "=" * 50)
print("STEP 4: Adding Memory")
print("=" * 50)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# Create chat LLM
chat_llm = ChatOllama(model="tinyllama:latest", temperature=0.3)

# Simple conversation history
chat_history = []

# Function to chat with history
def chat_with_history(message, history):
    # Add system context
    messages = [SystemMessage(content="You are a helpful assistant.")]
    
    # Add history
    for h in history:
        messages.append(HumanMessage(content=h))
    
    # Add current message
    messages.append(HumanMessage(content=message))
    
    # Get response
    response = chat_llm.invoke(messages)
    
    # Update history
    history.append(message)
    history.append(response.content)
    
    return response.content, history

# First question
resp1, chat_history = chat_with_history("My name is Kai!", chat_history)
print(f"Q1: My name is Kai!")
print(f"A1: {resp1}")

# Second question - references history
resp2, chat_history = chat_with_history("What's my name?", chat_history)
print(f"Q2: What's my name?")
print(f"A2: {resp2}")


# =============================================
# STEP 5: Creating a Chat Chain Class
# =============================================
print("\n" + "=" * 50)
print("STEP 5: Chat Chain Class")
print("=" * 50)

class ChatChain:
    """A simple chat chain with memory"""
    
    def __init__(self, llm, system_prompt="You are helpful."):
        self.llm = llm
        self.system = SystemMessage(content=system_prompt)
        self.history = []
    
    def chat(self, message):
        # Build messages
        messages = [self.system]
        
        # Add history
        for i in range(0, len(self.history), 2):
            if i < len(self.history):
                messages.append(HumanMessage(content=self.history[i]))
            if i + 1 < len(self.history):
                messages.append(self.history[i + 1])
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Get response
        response = self.llm.invoke(messages)
        
        # Save to history
        self.history.append(message)
        self.history.append(response.content)
        
        return response.content

# Use the class
chat_bot = ChatChain(chat_llm, "You are a friendly chatbot.")

print(chat_bot.chat("Hi! I'm learning AI."))
print(chat_bot.chat("What's my name?"))


# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 50)
print("SUMMARY - LCEL Basics")
print("=" * 50)
print("""
LCEL - LangChain Expression Language:

1. Chain: prompt | llm | parser
   - Output of one becomes input of next

2. Runnable Methods:
   - .invoke(input) - single call
   - .batch([inputs]) - multiple calls
   - .stream(input) - token by token

3. Memory: Keep conversation history
   - Store messages in a list
   - Pass full history to LLM each time

4. Class Pattern: Wrap in a class
   - Clean API
   - Persistent memory

Next Steps:
- Step 5: Tools and Agents in LangChain
""")
